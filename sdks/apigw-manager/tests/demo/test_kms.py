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

import base64
import builtins
import json
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives import padding as symmetric_padding
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from django.core.exceptions import ImproperlyConfigured

SETTINGS_PATH = Path(__file__).resolve().parents[2] / "demo" / "settings.py"


@pytest.fixture(scope="module")
def kms_private_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def credentials():
    return {
        "bkapp_id_secret": {
            "default": {"app_code": "$literal-app-code", "app_secret": "$literal-'\"\\\n密码 "},
            "bk_apigw_test": {"app_code": "test-app", "app_secret": "test-secret"},
        },
    }


@pytest.fixture
def envelope(monkeypatch, tmp_path, kms_private_key, credentials):
    path = tmp_path / "envelope"
    pem = kms_private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    monkeypatch.setenv("ENABLE_KMS", "true")
    monkeypatch.setenv("BK_APIGW_MANAGER_KMS_PRIVATE_KEY", base64.b64encode(pem).decode())
    monkeypatch.setenv("BK_APIGW_MANAGER_KMS_ENVELOPE_PATH", str(path))
    monkeypatch.delenv("BK_APIGW_MANAGER_KMS_APP_NAME", raising=False)
    monkeypatch.setenv("BK_APP_CODE", "legacy-app")
    monkeypatch.setenv("BK_APP_SECRET", "legacy-secret")

    def write(payload):
        plaintext = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        key, iv = os.urandom(16), os.urandom(16)
        encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
        ciphertext = iv + encryptor.update(plaintext.encode()) + encryptor.finalize()
        encrypted_key = kms_private_key.public_key().encrypt(
            key,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        content = {
            "asymmetric_type": "RSA",
            "symmetric_type": "AES",
            "symmetric_mode": "CTR",
            "encrypted_key": base64.b64encode(encrypted_key).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        }
        path.write_text(base64.b64encode(json.dumps(content).encode()).decode(), encoding="utf-8")
        return path

    write(credentials)
    return write


@pytest.mark.parametrize("flag", [None, "", "false", "False", "TRUE", " true"])
def test_disabled_keeps_legacy_credentials_without_loading_sdk(monkeypatch, tmp_path, flag):
    if flag is None:
        monkeypatch.delenv("ENABLE_KMS", raising=False)
    else:
        monkeypatch.setenv("ENABLE_KMS", flag)
    monkeypatch.setenv("BK_APP_CODE", "legacy-app")
    monkeypatch.setenv("BK_APP_SECRET", "legacy-secret")
    monkeypatch.setenv("BK_APIGW_MANAGER_KMS_ENVELOPE_PATH", str(tmp_path / "missing-envelope"))
    original_import = builtins.__import__

    def reject_sdk(name, *args, **kwargs):
        if name == "bk_kms":
            pytest.fail("KMS SDK must not be imported when disabled")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_sdk)
    loaded = runpy.run_path(str(SETTINGS_PATH))

    assert loaded["BK_APP_CODE"] == os.environ["BK_APP_CODE"] == "legacy-app"
    assert loaded["BK_APP_SECRET"] == os.environ["BK_APP_SECRET"] == "legacy-secret"


@pytest.mark.parametrize("flag", ["true", "True"])
@pytest.mark.parametrize("app_name", [None, "bk_apigw_test"])
def test_settings_and_environment_use_selected_literal_credentials(monkeypatch, envelope, credentials, flag, app_name):
    monkeypatch.setenv("ENABLE_KMS", flag)
    if app_name is not None:
        monkeypatch.setenv("BK_APIGW_MANAGER_KMS_APP_NAME", app_name)
    expected = credentials["bkapp_id_secret"][app_name or "default"]

    loaded = runpy.run_path(str(SETTINGS_PATH))

    assert loaded["BK_APP_CODE"] == os.environ["BK_APP_CODE"] == expected["app_code"]
    assert loaded["BK_APP_SECRET"] == os.environ["BK_APP_SECRET"] == expected["app_secret"]


@pytest.mark.parametrize("field", ["app_code", "app_secret"])
@pytest.mark.parametrize("bad_value", [None, "", "  ", 123, [], {}, "contains\x00nul"])
def test_invalid_credentials_block_initialization_without_partial_update(envelope, credentials, field, bad_value):
    credentials["bkapp_id_secret"]["default"][field] = bad_value
    envelope(credentials)

    with pytest.raises(ImproperlyConfigured, match=rf"bkapp_id_secret\.default\.{field}") as exc:
        runpy.run_path(str(SETTINGS_PATH))

    assert exc.value.__suppress_context__
    assert os.environ["BK_APP_CODE"] == "legacy-app"
    assert os.environ["BK_APP_SECRET"] == "legacy-secret"


@pytest.mark.parametrize("payload", [[], {}, {"bkapp_id_secret": []}, {"bkapp_id_secret": {"default": []}}])
def test_missing_credential_structure_blocks_initialization(envelope, payload):
    envelope(payload)

    with pytest.raises(ImproperlyConfigured, match=r"bkapp_id_secret\.default\.app_code"):
        runpy.run_path(str(SETTINGS_PATH))


@pytest.mark.parametrize(
    "variable",
    ["BK_APIGW_MANAGER_KMS_PRIVATE_KEY", "BK_APIGW_MANAGER_KMS_ENVELOPE_PATH", "BK_APIGW_MANAGER_KMS_APP_NAME"],
)
def test_empty_kms_configuration_blocks_initialization(monkeypatch, envelope, variable):
    monkeypatch.setenv(variable, " ")

    with pytest.raises(ImproperlyConfigured, match=variable):
        runpy.run_path(str(SETTINGS_PATH))


@pytest.mark.parametrize(
    "failure", ["missing-file", "invalid-envelope", "invalid-key", "invalid-json", "invalid-utf8"]
)
def test_invalid_inputs_fail_without_fallback_or_payload_in_errors(monkeypatch, envelope, credentials, failure):
    path = envelope(credentials)
    if failure == "missing-file":
        path.unlink()
    elif failure == "invalid-envelope":
        path.write_text("sensitive-invalid-envelope", encoding="utf-8")
    elif failure == "invalid-key":
        monkeypatch.setenv("BK_APIGW_MANAGER_KMS_PRIVATE_KEY", "sensitive-invalid-key")
    elif failure == "invalid-json":
        envelope("sensitive-invalid-json{")
    else:
        path.write_bytes(b"\xff")

    with pytest.raises(ImproperlyConfigured, match="KMS credential envelope") as exc:
        runpy.run_path(str(SETTINGS_PATH))

    assert "sensitive-" not in str(exc.value)
    assert exc.value.__suppress_context__
    assert os.environ["BK_APP_CODE"] == "legacy-app"
    assert os.environ["BK_APP_SECRET"] == "legacy-secret"


def test_missing_sdk_blocks_initialization(monkeypatch, envelope):
    original_import = builtins.__import__

    def reject_sdk(name, *args, **kwargs):
        if name == "bk_kms":
            raise ImportError("unavailable SDK")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_sdk)
    with pytest.raises(ImproperlyConfigured, match="bk-kms-sdk"):
        runpy.run_path(str(SETTINGS_PATH))


def test_unknown_app_name_does_not_fall_back_to_default(monkeypatch, envelope):
    monkeypatch.setenv("BK_APIGW_MANAGER_KMS_APP_NAME", "missing-app")

    with pytest.raises(ImproperlyConfigured, match=r"bkapp_id_secret\.missing-app\.app_code"):
        runpy.run_path(str(SETTINGS_PATH))


def test_unavailable_gm_backend_has_sanitized_error(monkeypatch, envelope):
    from bk_kms import CryptoBackendUnavailableError

    def fail_decrypt(**kwargs):
        raise CryptoBackendUnavailableError(
            backend="sensitive-backend", algorithms=["SM2"], platform="sensitive-platform"
        )

    monkeypatch.setattr("bk_kms.decrypt", fail_decrypt)
    with pytest.raises(ImproperlyConfigured, match="SM2/SM4 crypto backend is unavailable") as exc:
        runpy.run_path(str(SETTINGS_PATH))

    assert "sensitive-" not in str(exc.value)
    assert exc.value.__suppress_context__


@pytest.mark.parametrize("mode", ["CBC", "CTR"])
def test_sm2_sm4_envelope_initializes_literal_credentials(monkeypatch, envelope, credentials, mode):
    from bkcrypto import constants
    from bkcrypto.asymmetric.ciphers.sm2 import SM2AsymmetricCipher
    from bkcrypto.symmetric.ciphers.sm4 import SM4SymmetricCipher

    asymmetric_cipher = SM2AsymmetricCipher()
    key = os.urandom(16)
    plaintext = json.dumps(credentials, ensure_ascii=False).encode()
    if mode == "CBC":
        padder = symmetric_padding.PKCS7(128).padder()
        plaintext = padder.update(plaintext) + padder.finalize()
    symmetric_cipher = SM4SymmetricCipher(
        key=key,
        mode=constants.SymmetricMode(mode),
        padding=constants.SymmetricPadding.NONE,
    )
    content = {
        "asymmetric_type": "SM2",
        "symmetric_type": "SM4",
        "symmetric_mode": mode,
        "encrypted_key": asymmetric_cipher.encrypt_bytes(key),
        "ciphertext": symmetric_cipher.encrypt_bytes(plaintext),
    }
    path = Path(os.environ["BK_APIGW_MANAGER_KMS_ENVELOPE_PATH"])
    path.write_text(base64.b64encode(json.dumps(content).encode()).decode(), encoding="utf-8")
    monkeypatch.setenv(
        "BK_APIGW_MANAGER_KMS_PRIVATE_KEY", base64.b64encode(asymmetric_cipher.export_private_key().encode()).decode()
    )

    loaded = runpy.run_path(str(SETTINGS_PATH))

    expected = credentials["bkapp_id_secret"]["default"]
    assert loaded["BK_APP_CODE"] == os.environ["BK_APP_CODE"] == expected["app_code"]
    assert loaded["BK_APP_SECRET"] == os.environ["BK_APP_SECRET"] == expected["app_secret"]


def test_management_configuration_and_templates_use_decrypted_credentials(envelope, credentials):
    child_env = dict(os.environ, DJANGO_SETTINGS_MODULE="demo.settings", EXPECTED_CREDENTIALS=json.dumps(credentials))
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import json
import os
import django
django.setup()
from django.conf import settings
from django.template import Context, Template
from apigw_manager.apigw.command import DefinitionCommand
from apigw_manager.apigw.utils import get_configuration
expected = json.loads(os.environ['EXPECTED_CREDENTIALS'])['bkapp_id_secret']['default']
configuration = get_configuration()
assert configuration.bk_app_code == expected['app_code']
assert configuration.bk_app_secret == expected['app_secret']
context = DefinitionCommand().get_context([])
for setting, field in [('BK_APP_CODE', 'app_code'), ('BK_APP_SECRET', 'app_secret')]:
    assert getattr(settings, setting) == expected[field]
    for source in ['settings', 'environ']:
        template = Template('{{ ' + source + '.' + setting + ' }}')
        assert template.render(Context(context, autoescape=False)) == expected[field]
""",
        ],
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
