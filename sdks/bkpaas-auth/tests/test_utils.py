import pytest
from django.utils.timezone import now

from bkpaas_auth.utils import deserialize_datetime, scrub_data, serialize_datetime


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


def test_datetime_json_round_trip():
    value = now()
    assert deserialize_datetime(serialize_datetime(value)) == value
