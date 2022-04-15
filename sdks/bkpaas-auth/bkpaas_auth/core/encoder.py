# -*- coding: utf-8 -*-
import binascii
from typing import Tuple, Union

from bkpaas_auth.core.constants import ProviderType
from cryptography.hazmat.backends.openssl.backend import GetCipherByName, backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from six import ensure_binary, ensure_text


class _ARC4(algorithms.ARC4):
    """ARC4 should support key sizes bellow 40-2048 bits,
    but algorithms.ARC4 only support the kes size to be in [40, 56, 64, 80, 128, 160, 192, 256] bytes.

    In order to support the key='jdvoqu3o4', we must overwrite the field `key_sizes` to remove the restriction.
    This is the reason why we must implement another ARC4 algorithm.
    """

    key_sizes = frozenset(range(40, 2049, 4))


backend.register_cipher_adapter(_ARC4, type(None), GetCipherByName("rc4"))


class BluekingUserIdEncoder:
    """Generator for blueking user id"""

    # It is not a real secret key, just for encoding the username
    secret_key = 'jdvoqu3o4'

    def encode(self, provider_type: Union[int, ProviderType], username: Union[str, bytes]):
        """Generate a hex string used as blueking user id

        :param provider_type: See constants.ProviderType
        :param username: User uin or user rtx username
        :returns: A hex string
        """
        id_prefix = ProviderType(provider_type).get_id_prefix()

        algorithm = _ARC4(ensure_binary(self.secret_key))
        cipher = Cipher(algorithm, mode=None)
        encryptor = cipher.encryptor()
        encoded = encryptor.update(ensure_binary(username))
        return id_prefix + ensure_text(binascii.hexlify(encoded))

    def decode(self, user_id: Union[str, bytes]) -> Tuple[int, str]:
        """Decode a given bk_user_id to the combination of (provider_type, username)

        :param str user_id: Blueking user id
        :returns: (provider_type, username)
        """
        _provider_type, username = user_id[:2], user_id[2:]
        provider_type = int(_provider_type)

        algorithm = _ARC4(ensure_binary(self.secret_key))
        cipher = Cipher(algorithm, mode=None)
        decryptor = cipher.decryptor()
        decoded = decryptor.update(binascii.unhexlify(username))
        return provider_type, ensure_text(decoded)


user_id_encoder = BluekingUserIdEncoder()
