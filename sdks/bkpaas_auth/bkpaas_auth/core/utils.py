# -*- coding: utf-8 -*-
import random
import string

DFT_RANDOM_CHARACTER_SET = string.ascii_lowercase + string.digits


def generate_random_token(length=30, chars=DFT_RANDOM_CHARACTER_SET):
    """Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
