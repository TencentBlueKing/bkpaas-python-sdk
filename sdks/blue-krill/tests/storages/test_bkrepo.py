# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
from tempfile import SpooledTemporaryFile
from unittest import mock
from urllib.parse import urljoin

import pytest
import requests
import requests_mock
from requests.auth import HTTPBasicAuth

from blue_krill.contextlib import nullcontext as does_not_raise
from blue_krill.storages.blobstore.bkrepo import BKGenericRepo, BKRepoManager
from blue_krill.storages.blobstore.exceptions import ObjectAlreadyExists, UploadFailedError
from tests.utils import generate_random_string


@pytest.fixture()
def username():
    return generate_random_string()


@pytest.fixture()
def password():
    return generate_random_string()


@pytest.fixture()
def endpoint():
    return "http://dummy.com"


@pytest.fixture()
def session():
    return requests.session()


@pytest.fixture()
def adapter(session):
    adapter = requests_mock.Adapter()
    session.mount("http://", adapter)
    return adapter


@pytest.fixture()
def project():
    return "dummy-project"


@pytest.fixture()
def tenant_id():
    return "test-tenant-123"


@pytest.fixture()
def store(session, username, password, endpoint, project, tenant_id):
    store = BKGenericRepo(
        bucket="dummy-bucket",
        username=username,
        password=password,
        project=project,
        endpoint_url=endpoint,
        tenant_id=tenant_id,
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
    def test_upload(self, store, adapter, endpoint, project, tenant_id, allow_overwrite, fake_response, expected):
        key = "dummy-key"
        adapter.register_uri(
            "PUT", urljoin(endpoint, f"/generic/{tenant_id}_{project}/dummy-bucket/{key}"), json=fake_response
        )
        with expected:
            store.upload_fileobj(io.BytesIO(), key=key, allow_overwrite=allow_overwrite)

    def test_download(self, store, adapter, endpoint, mktemp, project, tenant_id):
        key = "dummy-key"
        expected = generate_random_string().encode()
        adapter.register_uri(
            "GET", urljoin(endpoint, f"/generic/{tenant_id}_{project}/dummy-bucket/{key}"), body=io.BytesIO(expected)
        )
        with open(store.download_file(key, filepath=mktemp()), "rb") as fh:
            assert fh.read() == expected

    def test_download_fileobj(self, store, adapter, endpoint, mktemp, project, tenant_id):
        key = "dummy-key"
        expected = generate_random_string().encode()
        adapter.register_uri(
            "GET", urljoin(endpoint, f"/generic/{tenant_id}_{project}/dummy-bucket/{key}"), body=io.BytesIO(expected)
        )
        with SpooledTemporaryFile() as fh:
            store.download_fileobj(key, fh=fh)
            fh.seek(0)
            assert fh.read() == expected

    def test_delete_file(self, store, adapter, endpoint, project, tenant_id):
        key = "dummy-key"
        adapter.register_uri(
            "DELETE",
            urljoin(endpoint, f"/generic/{tenant_id}_{project}/dummy-bucket/{key}"),
            json={"code": 0, "message": None, "data": None, "traceId": ""},
        )
        assert store.delete_file(key) is None

    def test_get_file_metadata(self, store, adapter, endpoint, mktemp, project, tenant_id):
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
        adapter.register_uri(
            "HEAD", urljoin(endpoint, f"/generic/{tenant_id}_{project}/dummy-bucket/{key}"), headers=mock_headers
        )
        assert store.get_file_metadata(key) == mock_headers

    def test_generate_random_string(self, store, adapter, endpoint):
        key = "dummy-key"
        expected = generate_random_string()
        adapter.register_uri(
            "POST",
            urljoin(endpoint, "/generic/temporary/url/create"),
            json={"code": 0, "message": "", "data": [{"url": urljoin(endpoint, expected)}]},
        )
        assert store.generate_presigned_url(key, expires_in=3600) == urljoin(endpoint, expected)


class TestBKRepoManager:
    """BKRepoManager 测试类"""

    @pytest.fixture()
    def manager(self, session, username, password, endpoint):
        return BKRepoManager(
            endpoint_url=endpoint,
            username=username,
            password=password,
            tenant_id="test-tenant-123",
        )

    @pytest.fixture()
    def manager_without_tenant(self, session, username, password, endpoint):
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
