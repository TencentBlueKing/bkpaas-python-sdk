# -*- coding: utf-8 -*-
import pytest

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.encoder import user_id_encoder


class TestUserIdGeneration:
    @pytest.mark.parametrize(
        ("input", "expected_encoded"),
        [
            ((1, "3"), "$$013"),
            ((ProviderType.UIN, "3"), "$$013"),
            ((2, "r"), "$$02r"),
            ((ProviderType.RTX, "r"), "$$02r"),
            ((1, "blueking"), "$$01blueking"),
            ((9, "admin"), "$$09admin"),
        ],
    )
    def test_encode(self, input, expected_encoded):
        assert user_id_encoder.encode(*input) == expected_encoded

    @pytest.mark.parametrize(
        ("input", "expected_encoded"),
        [
            ("0167", (1, "3")),
            ("0167", (ProviderType.UIN, "3")),
            ("0226", (2, "r")),
            ("0226", (ProviderType.RTX, "r")),
            ("0136c4ff90974290a7", (1, "blueking")),
            ("0935cce79c92", (9, "admin")),
            # 新的规则生成的用户信息也能正常解密
            ("$$01a47dea7cb11a11ef89645254009504dc", (1, "a47dea7cb11a11ef89645254009504dc")),
            ("$$013", (1, "3")),
            ("$$013", (ProviderType.UIN, "3")),
            ("$$02r", (2, "r")),
            ("$$02r", (ProviderType.RTX, "r")),
            ("$$01blueking", (1, "blueking")),
            ("$$09admin", (9, "admin")),
        ],
    )
    def test_decode(self, input, expected_decoded):
        assert user_id_encoder.decode(input) == expected_decoded
