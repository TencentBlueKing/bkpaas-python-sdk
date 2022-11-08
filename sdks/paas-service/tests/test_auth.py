# -*- coding: utf-8 -*-
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
        token = jwt.encode(payload, key='invald-secret', algorithm='HS256').decode()
        request = rf.request(QUERY_STRING=f"token={token}")
        request.session = {}

        with pytest.raises(InstanceAuthFailed):
            InstanceAuthBackend().invoke(request)

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_expired_token(self, rf, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() - 3600}
        token = jwt.encode(payload, key='foobar', algorithm='HS256').decode()
        request = rf.request(QUERY_STRING=f"token={token}")
        request.session = {}

        with pytest.raises(InstanceAuthFailed):
            InstanceAuthBackend().invoke(request)

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_normal_token(self, rf, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() + 3600}
        token = jwt.encode(payload, key='foobar', algorithm='HS256').decode()
        request = rf.request(QUERY_STRING=f"token={token}")
        request.session = {}

        invoked_instance = InstanceAuthBackend().invoke(request)
        assert invoked_instance.uuid == instance.uuid
