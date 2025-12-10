import pytest

from bkpaas_auth.utils import scrub_data


@pytest.mark.parametrize(
    ("input", "output"),
    [
        # Data remain intact
        ({"obj": {"value": 3}}, {"obj": {"value": 3}}),
        ("obj=foobar", "obj=foobar"),
        # Case-insensitive
        ({"Password": "bar"}, {"Password": "******"}),
        # Sensitive data at top level
        ({"name": "foo", "bk_ticket": "bar"}, {"name": "foo", "bk_ticket": "******"}),
        # Sensitive data at inside level
        (
            {"nested": {"l2": {"name": "foo", "bk_ticket": "bar"}}, "l1": 0},
            {"nested": {"l2": {"name": "foo", "bk_ticket": "******"}}, "l1": 0},
        ),
    ],
)
def test_scrub_data(input, output):
    assert scrub_data(input) == output
