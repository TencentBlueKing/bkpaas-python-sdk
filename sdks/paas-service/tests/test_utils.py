# -*- coding: utf-8 -*-
import pytest
from paas_service.utils import parse_redirect_params


@pytest.mark.parametrize(
    "redirect_url, kwargs, expected",
    [
        ("foo.bar.baz?a=1", {}, ("foo.bar.baz", {"a": "1"})),
        ("foo.bar.baz?a=1", {"a": "2"}, ("foo.bar.baz", {"a": "2"})),
        ("instance.index?a=1&b=1&b=2&c=3", {}, ("instance.index", {"a": "1", "b": "2", "c": "3"})),
    ],
)
def test_parse_redirect_params(redirect_url, kwargs, expected):
    assert parse_redirect_params(redirect_url, **kwargs) == expected
