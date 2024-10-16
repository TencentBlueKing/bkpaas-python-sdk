# -*- coding: utf-8 -*-
import binascii
from typing import Tuple, Union

from six import ensure_binary, ensure_text

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.algorithms import ARC4


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

        encoded = ARC4(ensure_binary(self.secret_key)).encrypt(ensure_binary(username))
        return id_prefix + ensure_text(binascii.hexlify(encoded))

    def decode(self, user_id: Union[str, bytes]) -> Tuple[int, str]:
        """Decode a given bk_user_id to the combination of (provider_type, username)

        :param str user_id: Blueking user id
        :returns: (provider_type, username)
        """
        _provider_type, username = user_id[:2], user_id[2:]
        provider_type = int(_provider_type)

        decoded = ARC4(ensure_binary(self.secret_key)).decrypt(binascii.unhexlify(username))
        return provider_type, ensure_text(decoded)


user_id_encoder = BluekingUserIdEncoder()
