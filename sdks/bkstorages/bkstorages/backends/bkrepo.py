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
from os import PathLike
from tempfile import SpooledTemporaryFile
from typing import Dict, List, Tuple

import curlify
import requests
from bkstorages.utils import get_setting, setting
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from requests.auth import HTTPBasicAuth
from six.moves.urllib_parse import urljoin

logger = logging.getLogger(__name__)


class RequestError(Exception):
    """服务请求异常"""

    def __init__(self, message, code="400", response=None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.response = response


class ObjectAlreadyExists(RequestError):
    """该对象已存在."""


class BKGenericRepoClient:
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
        self.bucket = bucket
        self.project = project
        # endpoint can not endswith '/'
        self.endpoint_url = endpoint_url.rstrip("/")
        self.username = username
        self.password = password

    def get_client(self) -> requests.Session:
        session = requests.session()
        session.auth = HTTPBasicAuth(username=self.username, password=self.password)
        return session

    def upload_file(self, filepath: PathLike, key: str, allow_overwrite: bool = True, **kwargs):
        """上传通用制品文件

        :param PathLike filepath: 需要上传文件的路径
        :param str key: 文件完整路径
        :param bool allow_overwrite: 是否覆盖已存在文件
        """
        with open(filepath, "rb") as fh:
            self.upload_fileobj(fh, key=key, allow_overwrite=allow_overwrite, **kwargs)

    def upload_fileobj(self, fh, key: str, allow_overwrite: bool = True, **kwargs):
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
        # ditry-code: fix the file with missing file name will be ignored by requests
        fh = File(file=fh, name=getattr(fh, "name", key) or key)

        try:
            resp = client.put(url, headers=headers, data=fh)
            self._validate_resp(resp)
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
        resp = client.get(url, stream=True)
        if not resp.ok:
            raise RequestError(str("system error"), code=str(resp.status_code), response=resp)
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
        resp = client.delete(url)
        self._validate_resp(resp)

    def get_file_metadata(self, key: str, *args, **kwargs) -> Dict:
        """具体返回值请看 bk-repo 的文档."""
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        resp = client.head(url)
        if resp.status_code == 200:
            return dict(resp.headers)
        raise RequestError("Can't get file head info", code=resp.status_code, response=resp)

    def generate_presigned_url(self, key: str, expires_in: int, token_type: str = "DOWNLOAD", *args, **kwargs) -> str:
        """创建临时访问url

        :param str key: 授权路径
        :param int expires_in: token 有效时间，单位秒，小于等于 0 则永久有效
        :param str token_type: token类型。UPLOAD:允许上传, DOWNLOAD: 允许下载, ALL: 同时允许上传和下载。
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, '/generic/temporary/url/create')

        resp = client.post(
            url,
            json={
                'projectId': self.project,
                'repoName': self.bucket,
                'fullPathSet': [key],
                'expireSeconds': expires_in,
                'type': token_type,
            },
        )
        try:
            data = self._validate_resp(resp)
            return data[0]["url"]
        except RequestError as e:
            logger.exception("生成 bkrepo 访问链接时出现异常")
            if str(e.code) != '250102':
                raise
            logger.warning("BKREPO中不存在该文件, 避免报错仅拼接 url ")
            return urljoin(self.endpoint_url, f'/generic/temporary/token/download/{self.project}/{self.bucket}/{key}')

    def list_dir(self, key_prefix: str) -> Tuple[List, List]:
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        cur_page = 0
        directories, files = [], []
        while True:
            cur_page += 1
            ds, fs, next_page = self.__list_dir(key_prefix, cur_page=cur_page)
            directories.extend(ds)
            files.extend(fs)
            if not next_page:
                break
        return directories, files

    def __list_dir(self, key_prefix: str, cur_page: int = 1) -> Tuple[List, List, bool]:
        """List objs stored in bk-repo, using pagination, returning a 3-tuple of lists;
        the first item being directories, the second item being files, the third item meaning any more page
        """
        directories, files = [], []
        client = self.get_client()
        url = urljoin(self.endpoint_url, f"/repository/api/node/page/{self.project}/{self.bucket}/{key_prefix}")
        # NOTE: 按分页查询 bkrepo 的文件数, 1000 是一个经验值, 设置仅可能大的数值是避免发送太多次请求到 bk-repo
        params = {"pageSize": 1000, "PageNumber": cur_page, "includeFolder": True}
        resp = client.get(url, params=params)
        data = self._validate_resp(resp)
        total_pages = data["totalPages"]
        for record in data["records"]:
            if record["folder"]:
                directories.append(record["name"])
            else:
                files.append(record["name"])
        return directories, files, (cur_page < total_pages)

    @staticmethod
    def _validate_resp(response: requests.Response) -> Dict:
        """校验响应体"""
        try:
            logger.debug("Equivalent curl command: %s", curlify.to_curl(response.request))
        except Exception:  # pylint: disable=broad-except
            pass

        try:
            data = response.json()
        except Exception as e:
            raise RequestError(str(e), code="Unknown", response=response) from e

        if data.get("code") != 0:
            raise RequestError(data.get("message"), code=data.get("code"), response=response)
        return data.get("data", {})


class BKRepoFile(File):
    def __init__(self, name, storage: 'BKRepoStorage'):
        """# type: (str, BKRepoStorage) -> None"""
        self.name = name
        self._storage = storage
        self._file = None
        self._dirty = False

    def _get_file(self):
        if self._file is None:
            self._file = SpooledTemporaryFile()
            self._storage.client.download_fileobj(key=self.name, fh=self._file)
            self._file.seek(0)
            self._dirty = False
        return self._file

    file = property(_get_file)

    def write(self, s):
        if not self.file:
            # NOTE: 必须先判断是否可以获取到 file 属性, 否则 _dirty 可能会被覆盖
            raise RuntimeError("File not found")
        self._dirty = True
        return self.file.write(s)

    def writelines(self, iterable):
        if not self.file:
            # NOTE: 必须先判断是否可以获取到 file 属性, 否则 _dirty 可能会被覆盖
            raise RuntimeError("File not found")
        self._dirty = True
        return super().writelines(iterable)

    def flush(self):
        super().flush()
        if self._dirty and self._file:
            flag = self._file.tell()
            self._file.seek(0)
            # 覆盖, 目前不支持增量上传
            self._storage.client.upload_fileobj(fh=self._file, key=self.name)
            self._file.seek(flag)

    def close(self):
        if self._file is None:
            return
        if self._dirty:
            self.flush()
        self._file.close()
        self._file = None


@deconstructible
class BKRepoStorage(Storage):
    """bkrepo Storage class for Django pluggable storage system."""

    location = setting('BKREPO_LOCATION', '')
    file_overwrite = setting('BKREPO_FILE_OVERWRITE', True)

    endpoint_url = get_setting('BKREPO_ENDPOINT_URL')
    username = get_setting('BKREPO_USERNAME')
    password = get_setting('BKREPO_PASSWORD')
    project_id = get_setting('BKREPO_PROJECT')
    bucket = get_setting('BKREPO_BUCKET')

    CHUNK_SIZE = 4 * 1024 * 1024

    def __init__(
        self,
        root_path=location,
        username=username,
        password=password,
        project_id=project_id,
        bucket=bucket,
        endpoint_url=endpoint_url,
        file_overwrite=file_overwrite,
    ):
        if any(v is None for v in [username, password, project_id, bucket, endpoint_url]):
            raise ImproperlyConfigured("please provide valid username、password、project_id、bucket and endpoint_url.")

        # 存储相关的配置
        self.root_path = root_path
        self.file_overwrite = file_overwrite
        # 基础配置
        self.endpoint_url = endpoint_url
        self.client = BKGenericRepoClient(
            bucket=bucket, project=project_id, username=username, password=password, endpoint_url=endpoint_url
        )

    def _full_path(self, name):
        if name == '/':
            name = ''
        return urljoin(self.root_path, name).replace('\\', '/')

    def _open(self, name, mode='rb'):
        return BKRepoFile(self._full_path(name), self)

    def _save(self, name, content):
        key = self._full_path(name)
        self.client.upload_fileobj(fh=content, key=key)
        return key

    def delete(self, name):
        self.client.delete_file(self._full_path(name))

    def exists(self, name):
        try:
            return bool(self.client.get_file_metadata(self._full_path(name)))
        except RequestError:
            return False

    def size(self, name):
        metadata = self.client.get_file_metadata(self._full_path(name))
        return metadata.get("Content-Length", 0)

    def url(self, name):
        # expires_in 小于等于 0 则永久有效
        return self.client.generate_presigned_url(self._full_path(name), expires_in=0)

    def listdir(self, path):
        return self.client.list_dir(self._full_path(name=path))

    # 上传文件相关
    def get_valid_name(self, name):
        """
        Returns a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return super().get_valid_name(name)

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        return super().get_available_name(name, max_length)

    def generate_filename(self, filename):
        """
        Validate the filename by calling get_valid_name() and return a filename
        to be passed to the save() method.
        """
        return super().generate_filename(filename)

    # 获取文件时间属性
    def get_accessed_time(self, name):
        # NOTE: bk-repo 不支持获取访问时间
        return self.get_modified_time(name)

    def get_created_time(self, name):
        # NOTE: bk-repo 不支持获取创建时间
        return self.get_modified_time(name)

    def get_modified_time(self, name):
        metadata = self.client.get_file_metadata(self._full_path(name))
        return metadata.get("Last-Modified", 0)

    # [Deprecated Method]
    def accessed_time(self, name):
        return self.get_accessed_time(name)

    def created_time(self, name):
        return self.get_created_time(name)

    def modified_time(self, name):
        return self.get_modified_time(name)
