# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.


import base64
import io
import json
import logging
from tempfile import SpooledTemporaryFile
from typing import List, Sequence
from unittest import mock
from urllib.parse import urljoin

import pytest
import requests
import requests_mock
from requests.auth import HTTPBasicAuth

from blue_krill.contextlib import nullcontext as does_not_raise
from blue_krill.data_types.url import REDACTED_URL_PLACEHOLDER
from blue_krill.storages.blobstore.bkrepo import BKGenericRepo, BKRepoManager
from blue_krill.storages.blobstore.exceptions import DownloadFailedError, ObjectAlreadyExists, UploadFailedError
from tests.utils import assert_redacted, generate_random_string

# 脱敏后的认证请求头, 出现在日志中说明请求确实携带了认证信息且已被脱敏
MASKED_AUTH = "'Authorization: ******'"


def curl_fragments(method: str, url: str) -> List[str]:
    """日志中的等价 curl 命令应包含的关键信息"""
    # GET 是 curl 的默认方法, curlify>=3.0 生成命令时会省略 "-X GET"
    command = "curl" if method == "GET" else f"curl -X {method}"
    return [command, MASKED_AUTH, url]


@pytest.fixture(autouse=True)
def _capture_all_logs(caplog):
    # 捕获所有级别的日志, 确保任何级别的日志中都不包含凭证信息
    caplog.set_level(logging.DEBUG)


@pytest.fixture
def username():
    return generate_random_string()


@pytest.fixture
def password():
    return generate_random_string()


@pytest.fixture
def credentials(username, password):
    """可能泄露到日志中的凭证: 密码本身及 Basic 认证请求头的值"""
    return [password, base64.b64encode(f"{username}:{password}".encode()).decode()]


@pytest.fixture
def check_logs(caplog, credentials):
    """检查日志中包含所有期望的信息, 且不包含任何凭证"""

    def _check(*expected: str, extra_secrets: Sequence[str] = ()):
        assert_redacted(caplog.text, secrets=[*credentials, *extra_secrets], expected=expected)

    return _check


@pytest.fixture
def endpoint():
    return "http://dummy.com"


@pytest.fixture
def session():
    return requests.session()


@pytest.fixture
def adapter(session):
    adapter = requests_mock.Adapter()
    session.mount("http://", adapter)
    return adapter


@pytest.fixture
def project():
    return "dummy-project-id"


@pytest.fixture
def object_url(endpoint, project):
    """返回制品文件的 URL"""

    def _object_url(key: str) -> str:
        return urljoin(endpoint, f"/generic/{project}/dummy-bucket/{key}")

    return _object_url


@pytest.fixture
def tenant_id():
    return "test-tenant-123"


@pytest.fixture
def store(session, username, password, endpoint, project):
    store = BKGenericRepo(
        bucket="dummy-bucket",
        username=username,
        password=password,
        project=project,
        endpoint_url=endpoint,
    )
    with mock.patch.object(store, "get_client", return_value=session):
        session.auth = HTTPBasicAuth(username=username, password=password)
        yield store


class TestBKGenericRepo:
    def test_auth(self, store, adapter, username, password, endpoint):
        adapter.register_uri("GET", endpoint, text="foo")
        resp = store.get_client().get(endpoint)
        assert resp.text == "foo"
        assert (
            resp.request.headers["Authorization"]
            == "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
        )

    @pytest.mark.parametrize(
        ("allow_overwrite", "fake_response", "expected"),
        [
            (True, {"code": 0, "message": ""}, does_not_raise()),
            (True, {"code": 1, "message": ""}, pytest.raises(UploadFailedError)),
            (False, {"code": 0, "message": ""}, does_not_raise()),
            (False, {"code": 250107, "message": ""}, pytest.raises(ObjectAlreadyExists)),
            (False, {"code": 251012, "message": ""}, pytest.raises(ObjectAlreadyExists)),
        ],
    )
    def test_upload(self, store, adapter, object_url, check_logs, allow_overwrite, fake_response, expected):
        url = object_url("dummy-key")
        adapter.register_uri("PUT", url, json=fake_response)
        with expected:
            store.upload_fileobj(io.BytesIO(), key="dummy-key", allow_overwrite=allow_overwrite)
        check_logs(*curl_fragments("PUT", url))

    def test_upload_with_bkapi_authorization(self, store, session, adapter, object_url, check_logs):
        """会话中携带的其他凭证类请求头同样不能出现在日志中"""
        app_secret = generate_random_string()
        session.headers["X-Bkapi-Authorization"] = json.dumps({"bk_app_code": "app", "bk_app_secret": app_secret})
        url = object_url("dummy-key")
        adapter.register_uri("PUT", url, json={"code": 0, "message": ""})

        store.upload_fileobj(io.BytesIO(), key="dummy-key")
        check_logs(*curl_fragments("PUT", url), "'X-Bkapi-Authorization: ******'", extra_secrets=[app_secret])

    def test_download(self, store, adapter, object_url, mktemp):
        key = "dummy-key"
        expected = generate_random_string().encode()
        adapter.register_uri("GET", object_url(key), body=io.BytesIO(expected))
        with open(store.download_file(key, filepath=mktemp()), "rb") as fh:
            assert fh.read() == expected

    def test_download_fileobj(self, store, adapter, object_url, check_logs):
        key = "dummy-key"
        url = object_url(key)
        expected = generate_random_string().encode()
        adapter.register_uri("GET", url, body=io.BytesIO(expected))
        with SpooledTemporaryFile() as fh:
            store.download_fileobj(key, fh=fh)
            fh.seek(0)
            assert fh.read() == expected
        check_logs(f"key: {key}", *curl_fragments("GET", url))

    def test_download_rejected(self, store, adapter, object_url, caplog, check_logs):
        key = "dummy-key"
        url = object_url(key)
        adapter.register_uri("GET", url, status_code=403, text="forbidden")
        with SpooledTemporaryFile() as fh, pytest.raises(DownloadFailedError):
            store.download_fileobj(key, fh=fh)

        check_logs(*curl_fragments("GET", url))
        (error_log,) = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
        assert "rejects the download request" in error_log
        assert f"key: {key}" in error_log
        assert url in error_log

    def test_download_key_with_at_sign(self, store, adapter, object_url, check_logs):
        # 路径中的 "@" 导致 URL 被整体替换为占位符, 需要单独记录 key 以便排查
        key = "pkg@1.0.0.tgz"
        adapter.register_uri("GET", object_url(key), text="foo")
        with SpooledTemporaryFile() as fh:
            store.download_fileobj(key, fh=fh)
        check_logs(f"key: {key}", MASKED_AUTH, REDACTED_URL_PLACEHOLDER)

    def test_delete_file(self, store, adapter, object_url, check_logs):
        url = object_url("dummy-key")
        adapter.register_uri("DELETE", url, json={"code": 0, "message": None, "data": None, "traceId": ""})
        assert store.delete_file("dummy-key") is None
        check_logs(*curl_fragments("DELETE", url))

    def test_get_file_metadata(self, store, adapter, object_url):
        key = "dummy-key"
        mock_headers = {
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Disposition": "attachment;filename=\"pytest.ini\";filename*=UTF-8''pytest.ini",
            "Content-Length": "9",
            "Content-Range": "bytes 0-8/9",
            "Content-Type": "application/octet-stream; charset=UTF-8",
            "Date": "Mon, 11 Jan 2021 12:48:47 GMT",
            "Etag": "8250d20f42b419af40706490ead78aabab9feba93eab09a3f626e3de5256e1f4",
            "Last-Modified": "Mon, 11 Jan 2021 12:47:54 GMT",
            "X-Proxy-By": "SmartGate-IDC",
            "X-Rio-Seq": "kjskbhxa-173749784",
        }
        adapter.register_uri("HEAD", object_url(key), headers=mock_headers)
        assert store.get_file_metadata(key) == mock_headers

    def test_generate_presigned_url(self, store, adapter, endpoint, check_logs):
        url = urljoin(endpoint, "/generic/temporary/url/create")
        expected = generate_random_string()
        adapter.register_uri(
            "POST", url, json={"code": 0, "message": "", "data": [{"url": urljoin(endpoint, expected)}]}
        )
        assert store.generate_presigned_url("dummy-key", expires_in=3600) == urljoin(endpoint, expected)
        check_logs(*curl_fragments("POST", url))


class TestBKRepoManager:
    """BKRepoManager 测试类"""

    @pytest.fixture
    def adapter(self):
        # get_client 每次都会创建新的 session, 因此需要全局 mock, 避免请求被发送到真实的网络中
        with requests_mock.Mocker() as m:
            yield m

    @pytest.fixture
    def manager(self, username, password, endpoint):
        return BKRepoManager(
            endpoint_url=endpoint,
            username=username,
            password=password,
            tenant_id="test-tenant-123",
        )

    @pytest.fixture
    def manager_without_tenant(self, username, password, endpoint):
        return BKRepoManager(
            endpoint_url=endpoint,
            username=username,
            password=password,
        )

    @pytest.mark.parametrize(
        ("method", "url_suffix", "data"),
        [
            ("post", "/auth/api/user/create/repo", {"projectId": "test", "repoName": "repo"}),
            ("put", "/auth/api/user/test-user", {}),
            ("delete", "/auth/api/user/test-user", None),
            ("post", "/repository/api/repo/create", {"projectId": "test", "name": "repo"}),
            ("delete", "/repository/api/repo/delete/test/repo", None),
            ("post", "/repository/api/project/create", {"name": "test"}),
        ],
    )
    def test_requests_have_tenant_header(self, manager, adapter, endpoint, method, url_suffix, data):
        """测试所有管理接口请求都携带租户ID头"""
        url = urljoin(endpoint, url_suffix)
        adapter.register_uri(method, url, json={"code": 0, "message": "ok"})

        client_method = getattr(manager.get_client(), method)
        resp = client_method(url, json=data)

        # 验证请求头中是否包含租户ID
        assert resp.request.headers["X-Bk-Tenant-Id"] == "test-tenant-123"

    def test_request_without_tenant_header(self, manager_without_tenant, adapter, endpoint):
        """测试未设置租户ID时不携带头信息"""
        url = urljoin(endpoint, "/repository/api/project/create")
        adapter.register_uri("POST", url, json={"code": 0, "message": "ok"})

        resp = manager_without_tenant.get_client().post(url, json={"name": "test"})

        assert "X-Bk-Tenant-Id" not in resp.request.headers

    @pytest.mark.parametrize(
        ("method", "http_method", "url_suffix", "extra_kwargs"),
        [
            ("create_user_to_repo", "POST", "/auth/api/user/create/repo", {"project": "p", "repo": "r"}),
            ("create_user_to_project", "POST", "/auth/api/user/create/project", {"project": "p"}),
            ("update_user", "PUT", "/auth/api/user/new-user", {}),
        ],
    )
    def test_user_password_not_logged(
        self, manager, adapter, endpoint, check_logs, method, http_method, url_suffix, extra_kwargs
    ):
        """请求体中的用户密码不能出现在日志中"""
        url = urljoin(endpoint, url_suffix)
        adapter.register_uri(http_method, url, json={"code": 0, "data": True})
        new_user_password = generate_random_string()

        getattr(manager, method)(
            username="new-user", password=new_user_password, association_users=["foo"], **extra_kwargs
        )
        check_logs(
            *curl_fragments(http_method, url),
            "'X-Bk-Tenant-Id: test-tenant-123'",
            extra_secrets=[new_user_password],
        )
