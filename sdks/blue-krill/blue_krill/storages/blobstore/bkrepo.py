# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import logging
from os import PathLike, getenv
from typing import Any, BinaryIO, List
from urllib.parse import urljoin

import curlify
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

from blue_krill.data_types.enum import EnumField, StructuredEnum
from blue_krill.storages.blobstore.base import BlobStore, ObjectAlreadyExists, RequestError, SignatureType

MAX_RETRIES = 2
logger = logging.getLogger(__name__)

TIMEOUT_THRESHOLD = float(getenv("BKREPO_TIMEOUT_THRESHOLD", 30))


def _validate_resp(response: requests.Response) -> Any:
    """校验响应体"""
    try:
        logger.debug("Equivalent curl command: %s", curlify.to_curl(response.request))
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
    """蓝鲸 bkrepo 管理端"""

    def __init__(
        self,
        endpoint_url: str,
        username: str,
        password: str,
        **kwargs,
    ):
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

    def create_user_to_repo(
        self, username: str, password: str, association_users: List[str], project: str, repo: str
    ) -> bool:
        """创建用户到仓库管理员

        :params username str: 用户名
        :params password str: 密码
        :params association_users List[str]: 关联的真实用户
        :params repo str: 关联的仓库名称
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, '/auth/api/user/create/repo')
        data = {
            "admin": True,
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
        url = urljoin(self.endpoint_url, f'/auth/api/user/{username}')
        data = {"admin": True, "name": username, "pwd": password, "asstUsers": association_users}
        return _validate_resp(client.put(url, json=data, timeout=TIMEOUT_THRESHOLD))

    def delete_user(self, username: str):
        """删除用户"""
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/auth/api/user/{username}')
        return _validate_resp(client.delete(url, timeout=TIMEOUT_THRESHOLD))

    def create_repo(self, project: str, repo: str, repo_type: str = RepositoryType.GENERIC, public: bool = False):
        """创建仓库

        :param public bool: 是否公开读, 当 public 为 True 时, 代表公开读私有写; 当 public 为 False 时, 代表私有读写
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, '/repository/api/repo/create')
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

        :params repo str: 仓库名
        :params forced bool: 是否强制删除, 如果为false，当仓库中存在文件时，将无法删除仓库
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/repository/api/repo/delete/{project}/{repo}?forced={forced}')
        return _validate_resp(client.delete(url, timeout=TIMEOUT_THRESHOLD))

    # 以下是项目无关的管理接口

    def create_project(self, project: str):
        """创建项目

        :params project str: 项目名
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, "/repository/api/project/create")
        data = {"name": project, "displayName": project, "description": ""}
        return _validate_resp(client.post(url, json=data, timeout=TIMEOUT_THRESHOLD))

    def create_user_to_project(self, username: str, password: str, association_users: List[str], project: str) -> bool:
        """创建用户到项目管理员

        :params username str: 用户名
        :params password str: 密码
        :params association_users List[str]: 关联的真实用户
        :params project str: 关联的项目名称
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, '/auth/api/user/create/project')
        data = {
            "admin": True,
            "name": username,
            "pwd": password,
            "userId": username,
            "asstUsers": association_users,
            "group": False,
            "projectId": project,
        }
        return _validate_resp(client.post(url, json=data, timeout=TIMEOUT_THRESHOLD))


class BKGenericRepo(BlobStore):
    """蓝鲸通用二进制仓库."""

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

        :param PathLike filepath: 需要上传文件的路径
        :param str key: 文件完整路径
        :param bool allow_overwrite: 是否覆盖已存在文件
        """
        with open(filepath, "rb") as fh:
            self.upload_fileobj(fh, key=key, allow_overwrite=allow_overwrite, timeout=TIMEOUT_THRESHOLD, **kwargs)

    def upload_fileobj(self, fh: BinaryIO, key: str, allow_overwrite: bool = True, **kwargs):
        """上传通用制品文件

        :param BinaryIO fh: 文件句柄
        :param str key: 文件完整路径
        :param bool allow_overwrite: 是否覆盖已存在文件
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        headers = {
            # TODO: 是否需要上传 md5 或者 sha256?
            "X-BKREPO-OVERWRITE": str(allow_overwrite),
        }
        try:
            resp = client.put(url, headers=headers, data=fh, timeout=TIMEOUT_THRESHOLD)
            _validate_resp(resp)
        except RequestError as e:
            if not allow_overwrite:
                # NOTE: 由于 BKRepo 尚未定义具体的错误码, 因此只能认为服务端报 RequestError 时, 就是对象已存在
                raise ObjectAlreadyExists(e.message, e.code, e.response)
            raise

    def download_file(self, key: str, filepath: PathLike, *args, **kwargs) -> PathLike:
        """下载通用制品文件

        :param str key: 文件完整路径
        :param PathLike filepath: 文件下载的路径
        """
        with open(filepath, mode="wb") as fh:
            self.download_fileobj(key, fh)
        return filepath

    def download_fileobj(self, key: str, fh, *args, **kwargs):
        """下载通用制品文件

        :param str key: 文件完整路径
        :param IO fh: 文件句柄
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        resp = client.get(url, stream=True, timeout=TIMEOUT_THRESHOLD)
        if not resp.ok:
            _validate_resp(resp)
            raise RequestError(str("下载制品文件失败"), code=str(resp.status_code), response=resp)
        try:
            for chunk in resp.iter_content(chunk_size=512):
                if chunk:
                    fh.write(chunk)
        except Exception as e:
            raise RequestError(str(e), code=str(resp.status_code), response=resp) from e

    def delete_file(self, key: str, *args, **kwargs):
        """删除通用制品文件

        :param str key: 文件完整路径
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        resp = client.delete(url, timeout=TIMEOUT_THRESHOLD)
        return _validate_resp(resp)

    def get_file_metadata(self, key, *args, **kwargs):
        """获取通用制品文件头部信息

        :param str key: 文件完整路径
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        resp = client.head(url, timeout=TIMEOUT_THRESHOLD)
        if resp.status_code == 200:
            return resp.headers
        raise RequestError("Can't get file head info", code=str(resp.status_code), response=resp)

    def generate_presigned_url(
        self, key: str, expires_in: int, signature_type: SignatureType = SignatureType.DOWNLOAD, *args, **kwargs
    ) -> str:
        """创建临时访问url

        :param str key: 授权路径
        :param int expires_in: token 有效时间，单位秒，小于等于 0 则永久有效
        :param str signature_type: 签名类型。UPLOAD:允许上传, DOWNLOAD: 允许下载。
        :param str token_type: [deprecated] token类型。UPLOAD:允许上传, DOWNLOAD: 允许下载, ALL: 同时允许上传和下载。
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, '/generic/temporary/url/create')

        token_type = signature_type.value
        if "token_type" in kwargs:
            logger.warning("[token_type] is deprecated. Please use signature_type instead.")
            token_type = kwargs["token_type"]

        resp = client.post(
            url,
            json={
                'projectId': self.project,
                'repoName': self.bucket,
                'fullPathSet': [key],
                'expireSeconds': expires_in,
                'type': token_type,
            },
            timeout=TIMEOUT_THRESHOLD,
        )
        data = _validate_resp(resp)
        return data[0]["url"]
