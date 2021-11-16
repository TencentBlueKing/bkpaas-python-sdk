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
import jwt
import pytest


@pytest.fixture(autouse=True)
def mark_django_db(db):
    pass


@pytest.fixture()
def api_name(settings, faker):
    api_name = faker.pystr()
    settings.BK_APIGW_NAME = api_name
    return api_name


@pytest.fixture()
def private_key():
    return '''-----BEGIN RSA PRIVATE KEY-----
MIICWgIBAAKBgER92Clgmc3ikcLbSjZFo2jC4mA+aP/kNKRKMud3AlDY0mPVbEu3
LeHov93zmvy1s5k5XTBPeAdRybKODQ0/jHOeXOOflaynDKZWknD8/WmU0O64Z/Qf
IH7c1FhDYX1VUZhwPwpL0IxYJDIoCKzwBafPsIC4PUH+Lqyga3emP/v1AgMBAAEC
gYA/wvQAmTi2Da3qvCFbYvscZQk/1foD9xv2skivaQBT6XX7kM1Ps4lYXUh5RPbN
Og6nn1qcxe6UydQ+kLWf1sBWT8xJP34RNm93dkHzSteU8WdlVYGNQqQQxYQXaSpN
g8kXjMY8+EUaQkptdQTgcpT2ZCW0ZD0LSpmklsRPPSW0xQJBAIabP/RAhZRMY6Eu
I1JDkSeJSnp7QP/M0HOu6tBcKxVjApaX3RUxIxR8e7F4TEUgaMmsU5TIfkKtdnDS
wLmcHG8CQQCCQpOyN4WffT0marIbSIJViaQYbyQAW/qrgYZrHNMApmv3dklLefF1
nifIHHQn6IkzBZaN0EfRlp907lu9bWfbAkB8SzdO75VpTvBgkR4EhGewvlGLr+xh
SFrjt40UQUd3RCnLrQd03h6qeBgv1Al5e2fHcdzr8gbEwzAvFizoN4L5AkAwzA4W
WlRVbg5FYPz92Yjx0FFH0gLTm6FpNGmNoMuu16lkl8xXWQRKgof2oCondSZIldRT
pe3xpxJvNIfri5u3AkA5VTxp77yXQ7Bra/F3eyLzQ8VzhhjXes+jxb6imag2Ry9o
AuBDWd8zTFaIkV0Wl8BteGrMMfhLv0F9JxuDcZas
-----END RSA PRIVATE KEY-----'''


@pytest.fixture()
def public_key():
    return '''-----BEGIN PUBLIC KEY-----
MIGeMA0GCSqGSIb3DQEBAQUAA4GMADCBiAKBgER92Clgmc3ikcLbSjZFo2jC4mA+
aP/kNKRKMud3AlDY0mPVbEu3LeHov93zmvy1s5k5XTBPeAdRybKODQ0/jHOeXOOf
laynDKZWknD8/WmU0O64Z/QfIH7c1FhDYX1VUZhwPwpL0IxYJDIoCKzwBafPsIC4
PUH+Lqyga3emP/v1AgMBAAE=
-----END PUBLIC KEY-----'''


@pytest.fixture()
def public_key_context(api_name, public_key):
    from apigw_manager.apigw.models import Context

    context, _ = Context.objects.update_or_create(
        key=api_name,
        scope="public_key",
        defaults={
            "value": public_key,
        },
    )

    try:
        yield context
    finally:
        context.delete()


@pytest.fixture()
def public_key_in_db(public_key_context):
    return public_key_context.value


@pytest.fixture()
def jwt_algorithm():
    return "RS512"


@pytest.fixture()
def jwt_app(settings):
    return {
        'app_code': settings.BK_APP_CODE,
        'verified': True,
    }


@pytest.fixture()
def jwt_user():
    return {
        'username': 'admin',
        'source_type': 'default',
        'verified': True,
    }


@pytest.fixture()
def jwt_decoded(jwt_app, jwt_user):
    return {
        'app': jwt_app,
        'user': jwt_user,
    }


@pytest.fixture()
def jwt_header(api_name, jwt_algorithm):
    return {'alg': jwt_algorithm, 'kid': api_name, 'typ': 'JWT'}


@pytest.fixture()
def jwt_encoded(jwt_header, jwt_decoded, private_key):
    return jwt.encode(
        payload=jwt_decoded,
        key=private_key,
        algorithm=jwt_header["alg"],
        headers=jwt_header,
    )
