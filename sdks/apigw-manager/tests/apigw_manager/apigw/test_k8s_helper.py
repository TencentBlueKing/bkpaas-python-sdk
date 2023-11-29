import base64

import pytest
from kubernetes.client import V1ObjectMeta, V1Secret, exceptions

from apigw_manager.apigw.k8s_helper import SecretPublicKeyManager


@pytest.fixture()
def public_key(faker):
    return faker.pystr()


@pytest.fixture()
def public_key_secret(fake_gateway_name, public_key):
    return V1Secret(
        metadata=V1ObjectMeta(
            name="bk-apigateway-public-key",
            namespace="bk-apigateway",
        ),
        data={
            fake_gateway_name: base64.b64encode(public_key.encode()).decode(),
        },
    )


class TestSecretPublicKeyManager:
    @pytest.fixture(autouse=True)
    def _setup_manager(self, issuer, mocker, settings, public_key_secret):
        mocker.patch("kubernetes.config.load_incluster_config")
        settings.APIGW_JWT_PUBLIC_KEY_SECRET_NAMESPACE = public_key_secret.metadata.namespace
        settings.APIGW_JWT_PUBLIC_KEY_SECRET_MAPPINGS = {
            issuer: public_key_secret.metadata.name,
        }

        self.manager = SecretPublicKeyManager()
        self.k8s_client = mocker.patch.object(self.manager, "client")

    def test_get_secret_not_exists(self, issuer, fake_gateway_name):
        self.k8s_client.read_namespaced_secret.side_effect = exceptions.ApiException(404)
        assert self.manager.get(fake_gateway_name, issuer) is None

    def test_get_public_key_not_found(self, issuer, public_key_secret):
        self.k8s_client.read_namespaced_secret.return_value = public_key_secret
        assert self.manager.get("not-found", issuer) is None

    def test_get(self, issuer, fake_gateway_name, public_key_secret):
        self.k8s_client.read_namespaced_secret.return_value = public_key_secret
        assert self.manager.get(fake_gateway_name, issuer)

    def test_set_for_create(self, issuer, fake_gateway_name, public_key):
        self.k8s_client.patch_namespaced_secret.side_effect = exceptions.ApiException(404)
        self.manager.set(fake_gateway_name, public_key, issuer)

        assert self.k8s_client.patch_namespaced_secret.call_count == 1
        assert self.k8s_client.create_namespaced_secret.call_count == 1

    def test_set_for_update(self, issuer, fake_gateway_name, public_key):
        self.k8s_client.patch_namespaced_secret.return_value = public_key_secret
        self.manager.set(fake_gateway_name, public_key, issuer)

        assert self.k8s_client.patch_namespaced_secret.call_count == 1
        assert self.k8s_client.create_namespaced_secret.call_count == 0
