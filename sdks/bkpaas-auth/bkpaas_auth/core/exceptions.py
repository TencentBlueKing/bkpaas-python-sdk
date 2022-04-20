# -*- coding: utf-8 -*-
"""Exceptions for bkpaas_auth module
"""


class ServiceError(Exception):
    """Login or Token service is not available"""


class InvalidSkeyError(Exception):
    """Invalid uin/skey given"""


class InvalidTokenCredentialsError(Exception):
    """When invalid credentials are given when exchange access token"""
