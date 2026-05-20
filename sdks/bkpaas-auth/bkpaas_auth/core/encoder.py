# -*- coding: utf-8 -*-
import binascii

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.algorithms import ARC4

def _ensure_binary(s: str | bytes) -> bytes:
    return s.encode("utf-8") if isinstance(s, str) else s

def _ensure_text(s: str | bytes) -> str:
    return s.decode("utf-8") if isinstance(s, bytes) else s

class BluekingUserIdEncoder:
    """Generator for blueking user id"""

    # It is not a real secret key, just for encoding the username
    secret_key = 'jdvoqu3o4'

    def encode(self, provider_type: int | ProviderType, username: str | bytes):
        """Generate a hex string used as blueking user id

        :param provider_type: See constants.ProviderType
        :param username: User uin or user rtx username
        :returns: A hex string
        """
        id_prefix = ProviderType(provider_type).get_id_prefix()

        encoded = ARC4(_ensure_binary(self.secret_key)).encrypt(_ensure_binary(username))
        return id_prefix + _ensure_text(binascii.hexlify(encoded))

    def decode(self, user_id: str | bytes) -> tuple[int, str]:
        """Decode a given bk_user_id to the combination of (provider_type, username)

        :param str user_id: Blueking user id
        :returns: (provider_type, username)
        """
        _provider_type, username = user_id[:2], user_id[2:]
        provider_type = int(_provider_type)

        decoded = ARC4(_ensure_binary(self.secret_key)).decrypt(binascii.unhexlify(username))
        return provider_type, _ensure_text(decoded)


user_id_encoder = BluekingUserIdEncoder()
