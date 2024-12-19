# -*- coding: utf-8 -*-
import random
import string

import mock
import requests

DFT_RANDOM_CHARACTER_SET = string.ascii_lowercase + string.digits


def mock_json_response(data):
    resp = mock.Mock()
    resp.status_code = 200
    resp.json.return_value = data
    return resp


def mock_raw_response(data):
    resp = requests.Response()
    resp.status_code = 200

    def to_json(**kwargs):
        return data

    setattr(resp, 'json', to_json)
    return resp


def generate_random_string(length=30, chars=DFT_RANDOM_CHARACTER_SET):
    """Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
