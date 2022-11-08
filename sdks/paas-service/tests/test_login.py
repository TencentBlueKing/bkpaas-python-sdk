# -*- coding: utf-8 -*-
import time

import jwt
import pytest
from django.conf import settings
from django.test.utils import override_settings
from django.urls.exceptions import NoReverseMatch
from paas_service.constants import REDIRECT_FIELD_NAME

pytestmark = pytest.mark.django_db
PAAS_SERVICE_JWT_CLIENTS = [{'iss': 'c1', 'key': 'foobar', 'algorithm': 'HS256'}]


def make_redirect_url(path):
    return f"{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}=http%3A//testserver{path}"


class TestAuthenticationViewSet:
    def test_no_user(self, client):
        resp = client.get("/authenticate/")
        assert resp.status_code == 302
        assert resp.url == make_redirect_url(resp.wsgi_request.path)

    def test_no_token(self, admin_client):
        resp = admin_client.get("/authenticate/")
        assert resp.status_code == 404

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_normal(self, admin_client, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() + 3600}
        token = jwt.encode(payload, key='foobar', algorithm='HS256').decode()
        # paas-service 默认重定向的视图名称为 instance.index, 需要由业务自行实现
        with pytest.raises(NoReverseMatch) as e:
            admin_client.get("/authenticate/", data={"token": token})

        assert e.match("Reverse for 'instance.index' not found")

    @override_settings(PAAS_SERVICE_JWT_CLIENTS=PAAS_SERVICE_JWT_CLIENTS)
    def test_redirect_url(self, admin_client, instance):
        payload = {'iss': 'c1', 'service_instance_id': str(instance.uuid), 'expires_at': time.time() + 3600}
        token = jwt.encode(payload, key='foobar', algorithm='HS256').decode()
        resp = admin_client.get("/authenticate/", data={"token": token, "redirect_url": "api.services.instance"})
        assert resp.status_code == 302
        assert resp.url == f"/instances/{instance.uuid}/"
