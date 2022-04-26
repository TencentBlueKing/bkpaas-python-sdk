# -*- coding: utf-8 -*-
import pytest

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.encoder import user_id_encoder


class TestUserIdGeneration:
    @pytest.mark.parametrize(
        "input, expected_encoded",
        [
            ((1, "3"), "0167"),
            ((ProviderType.UIN, "3"), "0167"),
            ((2, "r"), "0226"),
            ((ProviderType.RTX, "r"), "0226"),
            ((1, "blueking"), "0136c4ff90974290a7"),
            ((9, "admin"), "0935cce79c92"),
        ],
    )
    def test_encode(self, input, expected_encoded):
        assert user_id_encoder.encode(*input) == expected_encoded

    @pytest.mark.parametrize(
        "input, expected_decoded",
        [
            ("0167", (1, "3")),
            ("0167", (ProviderType.UIN, "3")),
            ("0226", (2, "r")),
            ("0226", (ProviderType.RTX, "r")),
            ("0136c4ff90974290a7", (1, "blueking")),
            ("0935cce79c92", (9, "admin")),
        ],
    )
    def test_decode(self, input, expected_decoded):
        assert user_id_encoder.decode(input) == expected_decoded
