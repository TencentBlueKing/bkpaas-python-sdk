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
import datetime
import logging
from os import PathLike
from tempfile import SpooledTemporaryFile
from typing import Dict, List, Tuple

import curlify
import requests
from bkstorages.exceptions import DownloadFailedError, ObjectAlreadyExists, RequestError, UploadFailedError
from bkstorages.utils import clean_name, get_available_overwrite_name, get_setting, safe_join, setting
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.timezone import localtime
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from six.moves.urllib_parse import urljoin

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
MAX_RETRIES = 2
logger = logging.getLogger(__name__)


TIMEOUT_THRESHOLD = float(get_setting("BKREPO_TIMEOUT_THRESHOLD") or 30)


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
            self.upload_fileobj(fh, key=key, allow_overwrite=allow_overwrite, **kwargs)

    def upload_fileobj(self, fh, key: str, allow_overwrite: bool = True, **kwargs):
        """上传通用制品文件

        :param BinaryIO fh: 文件句柄
        :param str key: 文件完整路径
        :param bool allow_overwrite: 是否覆盖已存在文件
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        src = getattr(fh, "name", "<memory>")
        headers = {"X-BKREPO-OVERWRITE": str(allow_overwrite)}

        try:
            resp = client.put(url, headers=headers, data=fh, timeout=TIMEOUT_THRESHOLD)
            self._validate_resp(resp)
        except RequestError as e:
            # 250107: 请求资源已经存在
            # 251012: Node Existed
            if str(e.code) in ["250107", "251012"]:
                raise ObjectAlreadyExists(e.message, e.code, e.response) from e
            logger.exception("Request success, but the server rejects the upload request.")
            raise UploadFailedError(key=key, src=src) from e
        except Exception as e:
            logger.exception("An unexpected exception occurred, detail: %s", e)
            raise UploadFailedError(key=key, src=src) from e

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
        dest = getattr(fh, "name", "<memory>")
        try:
            resp = client.get(url, stream=True, timeout=TIMEOUT_THRESHOLD)
            logger.info("Calling BkRepo, the equivalent curl command: %s", curlify.to_curl(resp.request))
        except Exception as e:
            logger.exception("Fail to init request to BkRepo when calling '%s'", url)
            raise DownloadFailedError(key=key, dest=dest) from e

        if not resp.ok:
            logger.exception("Request success, but the server rejects the download request.")
            raise DownloadFailedError(key=key, dest=dest) from RequestError(
                str("下载制品文件失败"), code=str(resp.status_code), response=resp
            )

        try:
            for chunk in resp.iter_content(chunk_size=512):
                if chunk:
                    fh.write(chunk)
        except Exception as e:
            logger.exception("File save failed, detail %s", e)
            raise DownloadFailedError(key=key, dest=dest) from e

    def delete_file(self, key: str, *args, **kwargs):
        """删除通用制品文件

        :param str key: 文件完整路径
        """
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        resp = client.delete(url, timeout=TIMEOUT_THRESHOLD)
        self._validate_resp(resp)

    def get_file_metadata(self, key: str, *args, **kwargs) -> Dict:
        """具体返回值请看 bk-repo 的文档."""
        client = self.get_client()
        url = urljoin(self.endpoint_url, f'/generic/{self.project}/{self.bucket}/{key}')
        resp = client.head(url, timeout=TIMEOUT_THRESHOLD)
        if resp.status_code == 200:
            return dict(resp.headers)
        raise RequestError("Can't get file head info", code=str(resp.status_code), response=resp)

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
            timeout=TIMEOUT_THRESHOLD,
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
        resp = client.get(url, params=params, timeout=TIMEOUT_THRESHOLD)
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
            logger.info("Equivalent curl command: %s", curlify.to_curl(response.request))
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
        cleaned_name = clean_name(name)
        # safe_join can not work with absolute path
        if cleaned_name.startswith("/"):
            cleaned_name = cleaned_name[1:]
        return safe_join(self.root_path, cleaned_name)

    def _open(self, name, mode='rb'):
        return BKRepoFile(self._full_path(name), self)

    def _save(self, name, content):
        if isinstance(content, File) and not content.name:
            content.name = name

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
        name = clean_name(name)
        if self.file_overwrite:
            return get_available_overwrite_name(name, max_length)
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
        raise NotImplementedError

    def get_created_time(self, name):
        # NOTE: bk-repo 不支持获取创建时间
        raise NotImplementedError

    def get_modified_time(self, name) -> datetime.datetime:
        metadata = self.client.get_file_metadata(self._full_path(name))

        gmt = metadata.get("Last-Modified")
        if gmt is None:
            raise NotImplementedError

        dt = parse_gmt_datetime(gmt)
        if setting('USE_TZ'):
            return localtime(dt)
        else:
            return dt

    # [Deprecated Method]
    def accessed_time(self, name):
        return self.get_accessed_time(name)

    def created_time(self, name):
        return self.get_created_time(name)

    def modified_time(self, name):
        return self.get_modified_time(name)


def parse_gmt_datetime(gmt: str) -> datetime.datetime:
    """从 gmt 字符串解析出 datetime.datetime
    >>> parse_gmt_datetime('Fri, 03 Dec 2021 10:55:04 GMT')
    datetime.datetime(2021, 12, 3, 10, 55, 4)
    """
    return datetime.datetime.strptime(gmt, GMT_FORMAT)
