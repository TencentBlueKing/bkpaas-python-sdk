# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
import time

import jwt
import pytest
from django.test.utils import override_settings
from paas_service.auth.backends import InstanceAuthBackend, InstanceAuthFailed

pytestmark = pytest.mark.django_db
PAAS_SERVICE_JWT_CLIENTS = [{'iss': 'c1', 'key': 'foobar', 'algorithm': 'HS256'}]


class TestInstanceAuthBackend:
    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_no_token(self, rf):
        request = rf.request()
        with pytest.raises(InstanceAuthFailed):
            InstanceAuthBackend().invoke(request)

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_token_invalid(self, rf, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() + 3600}
        token = jwt.encode(payload, key='invald-secret', algorithm='HS256')
        request = rf.request(QUERY_STRING=f"token={token}")
        request.session = {}

        with pytest.raises(InstanceAuthFailed):
            InstanceAuthBackend().invoke(request)

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_expired_token(self, rf, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() - 3600}
        token = jwt.encode(payload, key='foobar', algorithm='HS256')
        request = rf.request(QUERY_STRING=f"token={token}")
        request.session = {}

        with pytest.raises(InstanceAuthFailed):
            InstanceAuthBackend().invoke(request)

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_normal_token(self, rf, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() + 3600}
        token = jwt.encode(payload, key='foobar', algorithm='HS256')
        request = rf.request(QUERY_STRING=f"token={token}")
        request.session = {}

        invoked_instance = InstanceAuthBackend().invoke(request)
        assert invoked_instance.uuid == instance.uuid
