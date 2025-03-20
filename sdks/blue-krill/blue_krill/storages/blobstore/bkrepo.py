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

import logging
from os import PathLike, getenv
from typing import Any, BinaryIO, List, Optional
from urllib.parse import urljoin

import curlify
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

from blue_krill.data_types.enum import EnumField, StructuredEnum
from blue_krill.storages.blobstore.base import BlobStore, SignatureType
from blue_krill.storages.blobstore.exceptions import (
    DownloadFailedError,
    ObjectAlreadyExists,
    RequestError,
    UploadFailedError,
)

MAX_RETRIES = 2
logger = logging.getLogger(__name__)

TIMEOUT_THRESHOLD = float(getenv("BKREPO_TIMEOUT_THRESHOLD", "30"))


def _validate_resp(response: requests.Response) -> Any:
    """校验响应体"""
    try:
        logger.info("Calling BkRepo, the equivalent curl command: %s", curlify.to_curl(response.request))
    except Exception:  # pylint: disable=broad-except
        pass

    try:
        data = response.json()
    except Exception as e:  # pylint: disable=broad-except
        raise RequestError(str(e), code="Unknown", response=response) from e

    if data.get("code") != 0:
        raise RequestError(data.get("message"), code=data.get("code"), response=response)
    return data.get("data", {})


class RepositoryType(str, StructuredEnum):
    GENERIC = EnumField("GENERIC", label="通用二进制文件仓库")
    DOCKER = EnumField("DOCKER", label="Docker仓库")
    MAVEN = EnumField("MAVEN", label="Maven仓库")
    PYPI = EnumField("PYPI", label="Pypi仓库")
    NPM = EnumField("NPM", label="Npm仓库")
    HELM = EnumField("HELM", label="Helm仓库")
    COMPOSER = EnumField("COMPOSER", label="COMPOSER仓库")
    RPM = EnumField("RPM", label="Rpm仓库")


class BKRepoManager:
    """蓝鲸 bkrepo 管理端，提供创建项目、仓库、用户等功能。

    使用说明：多租户模式下需要传入租户 ID。
    示例：
    >>> manager = BKRepoManager(
    ...     endpoint_url="http://bkrepo.example.com",
    ...     username="admin",
    ...     password="blueking",
    ...     tenant_id="tenant-123"  # 多租户模式必填
    ... )
    >>> manager.create_project("myproject")  # 按目前 bk-repo 的规则，非多租户模式下，创建后的项目 ID 为 "myproject"; 多租户模式下, 创建后的项目ID为 "tenant-123-myproject"
    """

    def __init__(
        self,
        endpoint_url: str,
        username: str,
        password: str,
        tenant_id: Optional[str] = None,
        **kwargs,
    ):
        # endpoint can not endswith '/'
        self.endpoint_url = endpoint_url.rstrip("/")
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self._max_retries = kwargs.get("max_retries", MAX_RETRIES)

    def get_client(self) -> requests.Session:
        session = requests.session()
        session.auth = HTTPBasicAuth(username=self.username, password=self.password)
        if self.tenant_id:
            session.headers.update({"X-Bk-Tenant-Id": self.tenant_id})
        session.mount("http://", HTTPAdapter(max_retries=self._max_retries))
        session.mount("https://", HTTPAdapter(max_retries=self._max_retries))
        return session

    def create_user_to_repo(
        self, username: str, password: str, association_users: List[str], project: str, repo: str
    ) -> bool:
        """创建用户到仓库管理员

        :param username: 用户名
        :param password: 密码
        :param association_users: 关联的真实用户
        :param repo: 关联的仓库名称
        :param project: 项目 ID
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, "/auth/api/user/create/repo")
        data = {
            "admin": False,
            "name": username,
            "pwd": password,
            "userId": username,
            "asstUsers": association_users,
            "group": False,
            "projectId": project,
            "repoName": repo,
        }
        return _validate_resp(client.post(url, json=data, timeout=TIMEOUT_THRESHOLD))

    def update_user(self, username: str, password: str, association_users: List[str]):
        """更新用户信息"""
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/auth/api/user/{username}")
        data = {"admin": False, "name": username, "pwd": password, "asstUsers": association_users}
        return _validate_resp(client.put(url, json=data, timeout=TIMEOUT_THRESHOLD))

    def delete_user(self, username: str):
        """删除用户"""
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/auth/api/user/{username}")
        return _validate_resp(client.delete(url, timeout=TIMEOUT_THRESHOLD))

    def create_repo(self, project: str, repo: str, repo_type: str = RepositoryType.GENERIC, public: bool = False):
        """创建仓库

        :param public: 是否公开读, 当 public 为 True 时, 代表公开读私有写; 当 public 为 False 时, 代表私有读写
        :param project: 项目 ID
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, "/repository/api/repo/create")
        data = {
            "projectId": project,
            "name": repo,
            "type": RepositoryType(repo_type).value,
            "category": "LOCAL",
            "public": public,
            "description": "no description",
            "configuration": None,
            "storageCredentialsKey": None,
        }
        return _validate_resp(client.post(url, json=data, timeout=TIMEOUT_THRESHOLD))

    def delete_repo(self, project: str, repo: str, forced: bool = False):
        """删除仓库

        :param project: 项目 ID
        :param repo: 仓库名
        :param forced: 是否强制删除, 如果为false，当仓库中存在文件时，将无法删除仓库
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/repository/api/repo/delete/{project}/{repo}?forced={forced}")
        return _validate_resp(client.delete(url, timeout=TIMEOUT_THRESHOLD))

    # 以下是项目无关的管理接口

    def create_project(self, project_name: str):
        """创建项目

        :param project_name: 项目名称
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, "/repository/api/project/create")
        # Note: 创建项目时传的是项目名称，创建成功后 API 未返回项目 ID 信息
        # 按目前 bk-repo 的规则，启用/关闭多租户模式的情况下:
        # 关闭多租户: 项目 ID == 项目名称
        # 启用多租户: 项目 ID == f"{租户 ID}_{项目名称}"
        data = {"name": project_name, "displayName": project_name, "description": ""}
        return _validate_resp(client.post(url, json=data, timeout=TIMEOUT_THRESHOLD))

    def create_user_to_project(self, username: str, password: str, association_users: List[str], project: str) -> bool:
        """创建用户到项目管理员

        :param username: 用户名
        :param password: 密码
        :param association_users: 关联的真实用户
        :param project: 项目 ID
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, "/auth/api/user/create/project")
        data = {
            "admin": False,
            "name": username,
            "pwd": password,
            "userId": username,
            "asstUsers": association_users,
            "group": False,
            "projectId": project,
        }
        return _validate_resp(client.post(url, json=data, timeout=TIMEOUT_THRESHOLD))


class BKGenericRepo(BlobStore):
    """蓝鲸通用二进制仓库，提供通用制品上传、下载、删除等功能。"""

    STORE_TYPE = "bkrepo"

    def __init__(
        self,
        bucket: str,
        project: str,
        endpoint_url: str,
        username: str,
        password: str,
        **kwargs,
    ):
        super().__init__(bucket)
        self.project = project
        # endpoint can not endswith '/'
        self.endpoint_url = endpoint_url.rstrip("/")
        self.username = username
        self.password = password
        self._max_retries = kwargs.get("max_retries", MAX_RETRIES)

    def get_client(self) -> requests.Session:
        session = requests.session()
        session.auth = HTTPBasicAuth(username=self.username, password=self.password)
        session.mount("http://", HTTPAdapter(max_retries=self._max_retries))
        session.mount("https://", HTTPAdapter(max_retries=self._max_retries))
        return session

    def upload_file(self, filepath: PathLike, key: str, allow_overwrite: bool = True, **kwargs):
        """上传通用制品文件

        :param PathLike: 需要上传文件的路径
        :param key: 文件完整路径
        :param allow_overwrite: 是否覆盖已存在文件
        """
        with open(filepath, "rb") as fh:
            self.upload_fileobj(fh, key=key, allow_overwrite=allow_overwrite, timeout=TIMEOUT_THRESHOLD, **kwargs)

    def upload_fileobj(self, fh: BinaryIO, key: str, allow_overwrite: bool = True, **kwargs):
        """上传通用制品文件

        :param fh: 文件句柄
        :param key: 文件完整路径
        :param allow_overwrite: 是否覆盖已存在文件
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/generic/{self.project}/{self.bucket}/{key}")
        src = getattr(fh, "name", "<memory>")
        headers = {"X-BKREPO-OVERWRITE": str(allow_overwrite)}

        try:
            resp = client.put(url, headers=headers, data=fh, timeout=TIMEOUT_THRESHOLD)
            _validate_resp(resp)
        except RequestError as e:
            # 250107: 请求资源已经存在
            # 251012: Node Existed
            if str(e.code) in ["250107", "251012"]:
                raise ObjectAlreadyExists(e.message, e.code, e.response) from e
            logger.exception("Request success, but the server rejects the upload request.")
            raise UploadFailedError(key=key, src=src) from e
        except Exception as e:
            logger.exception("An unexpected exception occurred, detail: %s", e)  # noqa: TRY401
            raise UploadFailedError(key=key, src=src) from e

    def download_file(self, key: str, filepath: PathLike, *args, **kwargs) -> PathLike:
        """下载通用制品文件

        :param key: 文件完整路径
        :param filepath: 文件下载的路径
        """
        with open(filepath, mode="wb") as fh:
            self.download_fileobj(key, fh)
        return filepath

    def download_fileobj(self, key: str, fh, *args, **kwargs):
        """下载通用制品文件

        :param key: 文件完整路径
        :param fh: 文件句柄
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/generic/{self.project}/{self.bucket}/{key}")
        dest = getattr(fh, "name", "<memory>")
        try:
            resp = client.get(url, stream=True, timeout=TIMEOUT_THRESHOLD)
            logger.info("Calling BkRepo, the equivalent curl command: %s", curlify.to_curl(resp.request))
        except Exception as e:
            logger.exception("Fail to init request to BkRepo when calling '%s'", url)
            raise DownloadFailedError(key=key, dest=dest) from e

        if not resp.ok:
            logger.exception(
                "Request success, but the server rejects the download request, please check by those curl command: %s",
                curlify.to_curl(resp.request),
            )
            raise DownloadFailedError(key=key, dest=dest) from RequestError(
                str("下载制品文件失败"), code=str(resp.status_code), response=resp
            )

        try:
            for chunk in resp.iter_content(chunk_size=512):
                if chunk:
                    fh.write(chunk)
        except Exception as e:
            logger.exception("File save failed, detail %s", e)  # noqa: TRY401
            raise DownloadFailedError(key=key, dest=dest) from e

    def delete_file(self, key: str, *args, **kwargs):
        """删除通用制品文件

        :param key: 文件完整路径
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/generic/{self.project}/{self.bucket}/{key}")
        resp = client.delete(url, timeout=TIMEOUT_THRESHOLD)
        return _validate_resp(resp)

    def get_file_metadata(self, key, *args, **kwargs):
        """获取通用制品文件头部信息

        :param key: 文件完整路径
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/generic/{self.project}/{self.bucket}/{key}")
        resp = client.head(url, timeout=TIMEOUT_THRESHOLD)
        if resp.status_code == 200:
            return resp.headers
        raise RequestError("Can't get file head info", code=str(resp.status_code), response=resp)

    def generate_presigned_url(
        self, key: str, expires_in: int, signature_type: SignatureType = SignatureType.DOWNLOAD, *args, **kwargs
    ) -> str:
        """创建临时访问url

        :param key: 授权路径
        :param expires_in: token 有效时间，单位秒，小于等于 0 则永久有效
        :param signature_type: 签名类型。UPLOAD:允许上传, DOWNLOAD: 允许下载。
        :param token_type: [deprecated] token类型。UPLOAD:允许上传, DOWNLOAD: 允许下载, ALL: 同时允许上传和下载。
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, "/generic/temporary/url/create")

        token_type = signature_type.value
        if "token_type" in kwargs:
            logger.warning("[token_type] is deprecated. Please use signature_type instead.")
            token_type = kwargs["token_type"]

        resp = client.post(
            url,
            json={
                "projectId": self.project,
                "repoName": self.bucket,
                "fullPathSet": [key],
                "expireSeconds": expires_in,
                "type": token_type,
            },
            timeout=TIMEOUT_THRESHOLD,
        )
        data = _validate_resp(resp)
        return data[0]["url"]
