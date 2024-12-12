# -*- coding: utf-8 -*-
import binascii
from typing import Tuple, Union

from six import ensure_binary, ensure_text

from bkpaas_auth.core.algorithms import ARC4
from bkpaas_auth.core.constants import ProviderType


class BluekingUserIdEncoder:
    """Generator for blueking user id"""

    # Used to parse existing encrypted user IDs. New user IDs are no longer encrypted.
    # It is not a real secret key, just for encoding the username.
    secret_key = "jdvoqu3o4"
    # Flag indicating that the user ID is unencrypted.
    unencrypted_user_flag = "$$"

    def encode(self, provider_type: Union[int, ProviderType], username: Union[str, bytes]):
        """Encode the provider type and username into a Blueking user ID.

        :param provider_type: See constants.ProviderType
        :param username: The username format includes: uin (QQ login), username, uuid (latest user management rules)
        :return: A hex string representing the Blueking user ID.
        """
        id_prefix = ProviderType(provider_type).get_id_prefix()
        return self.unencrypted_user_flag + id_prefix + username

    def decode(self, user_id: Union[str, bytes]) -> Tuple[int, str]:
        """Decode a given Blueking user ID into its constituent provider type and username.

        :param str user_id: Blueking user id
        :returns: (provider_type, username)
        """
        # Check if the user ID is unencrypted
        if user_id.startswith(self.unencrypted_user_flag):
            user_info = user_id[2:]
            _provider_type, decoded_username = user_info[:2], user_info[2:]
        else:
            # Handle encrypted user ID
            _provider_type, encrypted_username = user_id[:2], user_id[2:]
            decoded = ARC4(ensure_binary(self.secret_key)).decrypt(binascii.unhexlify(encrypted_username))
            decoded_username = ensure_text(decoded)

        provider_type = int(_provider_type)
        return provider_type, decoded_username


user_id_encoder = BluekingUserIdEncoder()
