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
import os
import posixpath

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from django.utils.encoding import force_text
from six.moves.urllib.parse import urljoin


def setting(name, default=None, strict=False):
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it can return a default or raise an error if in strict mode.

    :param name: Name of setting
    :type name: str
    :param default: Value if setting is unfound
    :param strict: Define if return default value or raise an error
    :type strict: bool
    :returns: Setting's value
    :raises: django.core.exceptions.ImproperlyConfigured if setting is unfound
             and strict mode
    """
    if strict and not hasattr(settings, name):
        msg = "You must provide settings.%s" % name
        raise ImproperlyConfigured(msg)
    return getattr(settings, name, default)


def get_setting(names, allow_env=True):
    """Get settings from settings first, then find in env vars

    :param list names: possible variable names
    :param bool allow_env: search variable in system env vars or not, default to True
    """
    names = [names] if not isinstance(names, (list, tuple)) else names
    for name in names:
        value = setting(name)
        if value is not None:
            break

    if value is None and allow_env:
        for name in names:
            value = os.environ.get(name)
            if value is not None:
                break
    return value


def safe_join(base, *paths):
    """
    A version of django.utils._os.safe_join for S3 paths.

    Joins one or more path components to the base path component
    intelligently. Returns a normalized version of the final path.

    The final path must be located inside of the base path component
    (otherwise a ValueError is raised).

    Paths outside the base path indicate a possible security
    sensitive operation.
    """
    base_path = force_text(base)
    base_path = base_path.rstrip('/')
    paths = [force_text(p) for p in paths]

    final_path = base_path
    for path in paths:
        final_path = urljoin(final_path.rstrip('/') + "/", path)

    # Ensure final_path starts with base_path and that the next character after
    # the final path is '/' (or nothing, in which case final_path must be
    # equal to base_path).
    base_path_len = len(base_path)
    if not final_path.startswith(base_path) or final_path[base_path_len : base_path_len + 1] not in ('', '/'):
        raise ValueError('the joined path is located outside of the base path' ' component')

    return final_path.lstrip('/')


def clean_name(name):
    """
    Cleans the name so that Windows style paths work
    """
    # Normalize Windows style paths
    clean_name = posixpath.normpath(name).replace('\\', '/')

    # posixpath.normpath() can strip trailing slashes so we implement
    # a workaround here.
    if name.endswith('/') and not clean_name.endswith('/'):
        # Add a trailing slash as it was stripped.
        clean_name = clean_name + '/'

    # Given an empty string, posixpath.normpath() will return ., which we don't want
    if clean_name == '.' and name != ".":
        clean_name = ''

    return clean_name


def get_available_overwrite_name(name, max_length):
    """Return a filename that's meet the maximum length limit.
    If the name is too long, this function will try to truncate those overflow.

    >>> get_available_overwrite_name("foo/bar/baz.ext", max_length=12)
    Traceback (most recent call last):
        ...
    django.core.exceptions.SuspiciousFileOperation: ...

    >>> get_available_overwrite_name("foo/bar/baz.ext", max_length=13)
    'foo/bar/b.ext'

    >>> get_available_overwrite_name("foo/bar/baz.ext", max_length=14)
    'foo/bar/ba.ext'

    >>> get_available_overwrite_name("foo/bar/baz.ext", max_length=15)
    'foo/bar/bar.ext'

    >>> get_available_overwrite_name("foo/bar/baz.ext", max_length=None)
    'foo/bar/bar.ext'
    """
    if max_length is None or len(name) <= max_length:
        return name

    # Adapted from Django
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    truncation = len(name) - max_length

    file_root = file_root[:-truncation]
    if not file_root:
        raise SuspiciousFileOperation(
            'Storage can not truncate away entire filename for "%s". '
            'Please make sure that the corresponding file field '
            'allows sufficient "max_length".' % name
        )
    return os.path.join(dir_name, "{}{}".format(file_root, file_ext))
