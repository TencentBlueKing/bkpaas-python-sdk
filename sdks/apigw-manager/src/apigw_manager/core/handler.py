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

import json
import logging
import os
import typing

from bkapi.bk_apigateway.client import Client as BKAPIGatewayClient

from apigw_manager.core.exceptions import ApiException, ApiResponseError, ApiResultError
from bkapi_client_core.exceptions import ResponseError

if typing.TYPE_CHECKING:
    from apigw_manager.core import configuration  # noqa

logger = logging.getLogger(__name__)


class Handler(object):
    def __init__(self, config):
        self.config = config  # type: configuration.Configuration

        self.client = BKAPIGatewayClient(endpoint=config.host, stage=config.stage)

    def __post_init__(self):
        pass

    def _get_bkapi_authorization(self):
        """Get authentication information"""
        return json.dumps(
            {
                "bk_app_code": self.config.bk_app_code,
                "bk_app_secret": self.config.bk_app_secret,
                "access_token": self.config.access_token,
            }
        )

    def _get_from_cache(self, operation_id, data):
        api_cache = self.config.api_cache
        if not api_cache:
            return False, None

        return api_cache.try_get(operation_id, data)

    def _put_into_cache(self, operation_id, data, result):
        api_cache = self.config.api_cache
        if api_cache:
            api_cache.update(operation_id, data, result)
            return True

        return False

    def _call_with_cache(self, operation, **kwargs):
        """Call the API instance, allow data to be retrieved from the cache"""
        cache_key = {
            "gateway_name": kwargs.get("gateway_name", self.config.gateway_name),
            "kwargs": kwargs,
        }

        operation_id = operation.name
        cached, result = self._get_from_cache(operation_id, cache_key)
        if cached:
            return result

        result = self._call(operation, **kwargs)

        self._put_into_cache(operation_id, cache_key, result)

        return result

    def _get_tenant_id(self):
        """
        获取应用所属的租户 ID
        Note: BKPAAS_APP_TENANT_ID 和 BK_APP_TENANT_ID 的含义不一样
            BKPAAS_APP_TENANT_ID 是应用的租户模式标识，表示应用是全租户还是单租户
            BK_APP_TENANT_ID 是应用所属的租户 ID，表示应用是属于哪个租户的，即由哪个租户产生的
        """
        # [大多数是外部 SaaS 场景] PaaS 平台上部署运行的应用，会自动内置 BKPAAS_APP_TENANT_ID 环境变量，表示应用是全租户的还是单租户的
        paas_app_tenant_id = os.environ.get("BKPAAS_APP_TENANT_ID")
        if paas_app_tenant_id is not None:
            # 空字符串表示全租户应用，则返回 system，因为全租户应用只能在运营租户 (system) 下创建
            return paas_app_tenant_id or "system"

        # 对于单租户应用，BK_APP_TENANT_ID 可以不设置; 对于全租户应用，BK_APP_TENANT_ID 必须设置，建议设置为 system
        bk_app_tenant_id = self.config.bk_app_tenant_id or ""
        logger.warning(
            "[warn] if the syncing to apigateway failed, and your app(%s) is a global tenant app, please set the environment variable BK_APP_TENANT_ID to `system` (or set django settings.BK_APP_TENANT_ID to `system`) and try again. the current value [X-Bk-Tenant-Id=%s].",
            self.config.bk_app_code,
            bk_app_tenant_id,
        )
        return bk_app_tenant_id

    def _call(self, operation, files=None, **kwargs):
        """Call the API instance"""
        data = {
            "path_params": {"api_name": kwargs.pop("gateway_name", self.config.gateway_name)},
            "data": kwargs,
            "headers": {
                "X-Bkapi-Authorization": kwargs.pop("x_bkapi_authorization", self._get_bkapi_authorization()),
                # the header is required by the API gateway plugin bk-tenant-validate, for global tenant app!
                # so we set it to system, it would not be used in the gateway
                "X-Bk-Tenant-Id": self._get_tenant_id(),
            },
            "files": files,
        }

        operation_id = operation.name
        logger.debug("call api %s, data: %s", operation_id, data)

        try:
            return operation(**data)
        except ResponseError as err:
            message = "%s\n%s\nResponse: %s" % (err, err.curl_command, err.response_text)
            raise ApiResponseError(message)
        except Exception as err:
            raise ApiException(operation_id) from err

    def _call_v2(self, operation, files=None, **kwargs):
        """Call the API instance：
          - Uses "gateway_name" as the key in `path_params` instead of "api_name".
        """

        path_params = {"gateway_name": kwargs.pop("gateway_name", self.config.gateway_name)}
        if "{stage_name}" in operation.path:
            path_params["stage_name"] = kwargs.get("name")

        data = {
            "path_params": path_params,
            "data": kwargs,
            "headers": {
                "X-Bkapi-Authorization": kwargs.pop("x_bkapi_authorization", self._get_bkapi_authorization()),
                # the header is required by the API gateway plugin bk-tenant-validate, for global tenant app!
                # so we set it to system, it would not be used in the gateway
                "X-Bk-Tenant-Id": self._get_tenant_id(),
            },
            "files": files,
        }

        operation_id = operation.name
        logger.debug("call api %s, data: %s", operation_id, data)

        try:
            return operation(**data)
        except ResponseError as err:
            message = "%s\n%s\nResponse: %s" % (err, err.curl_command, err.response_text)
            raise ApiResponseError(message)
        except Exception as err:
            raise ApiException(operation_id) from err

    def _parse_result(self, result, convertor, code=0):
        """Check the code and convert the result"""
        logger.debug("code %s, message: %s", result.get("code"), result.get("message"))
        if result.get("code") != code:
            raise ApiResultError(
                result.get("code"),
                result.get("message"),
            )

        return convertor(result)
