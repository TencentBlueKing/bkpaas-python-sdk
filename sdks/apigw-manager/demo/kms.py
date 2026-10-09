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

"""Load application credentials for the image's bundled Django project."""

import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def load_app_credentials() -> tuple[str, str] | None:
    if os.environ.get("ENABLE_KMS") not in ("true", "True"):
        return None

    private_key = os.environ.get("BK_APIGW_MANAGER_KMS_PRIVATE_KEY", "").strip()
    if not private_key:
        raise ImproperlyConfigured("KMS requires BK_APIGW_MANAGER_KMS_PRIVATE_KEY")
    envelope_path = os.environ.get("BK_APIGW_MANAGER_KMS_ENVELOPE_PATH", "")
    if not envelope_path.strip():
        raise ImproperlyConfigured("KMS requires BK_APIGW_MANAGER_KMS_ENVELOPE_PATH")
    app_name = os.environ.get("BK_APIGW_MANAGER_KMS_APP_NAME", "default")
    if not app_name.strip():
        raise ImproperlyConfigured("KMS requires a non-empty BK_APIGW_MANAGER_KMS_APP_NAME")

    credentials = _decrypt_credentials(Path(envelope_path), private_key)
    values = {}
    for field in ("app_code", "app_secret"):
        path = ("bkapp_id_secret", app_name, field)
        value = credentials
        for part in path:
            value = value.get(part) if isinstance(value, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise ImproperlyConfigured(f"KMS requires a non-empty string at {'.'.join(path)}") from None
        if "\x00" in value:
            raise ImproperlyConfigured(f"KMS credential at {'.'.join(path)} cannot contain NUL") from None
        values[field] = value
    return values["app_code"], values["app_secret"]


def _decrypt_credentials(envelope_path: Path, private_key: str) -> object:
    try:
        from bk_kms import CryptoBackendUnavailableError, CryptoError, decrypt
    except ImportError:
        raise ImproperlyConfigured("KMS requires the bk-kms-sdk package; install the kms extra") from None

    try:
        envelope = envelope_path.read_text(encoding="utf-8").strip()
        return json.loads(decrypt(envelope=envelope, private_key=private_key))
    except CryptoBackendUnavailableError:
        raise ImproperlyConfigured("KMS SM2/SM4 crypto backend is unavailable; check the gm dependencies") from None
    except (OSError, UnicodeError, ValueError, CryptoError):
        # SDK and JSON exception details can contain credential material.
        raise ImproperlyConfigured(
            "Unable to read or decrypt the KMS credential envelope; check the file, private key and JSON payload"
        ) from None
