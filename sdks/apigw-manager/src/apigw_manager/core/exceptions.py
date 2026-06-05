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


class ApiException(Exception):
    def __init__(self, operation_id):
        self.operation_id = operation_id

    def __str__(self):
        return self.operation_id


class ApiResponseError(Exception):
    """There was an exception that occurred while handling the response"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ApiResultError(ApiResponseError):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "code: %s, %s" % (self.code, self.message)
