# -*- coding: utf-8 -*-
"""Exceptions for bkpaas_auth module
"""


class ServiceError(Exception):
    """Login or Token service is not available"""


class HttpRequestError(Exception):
    """http request error"""


class ResponseError(Exception):
    """service response error"""


class InvalidSkeyError(Exception):
    """Invalid uin/skey given"""


class InvalidTokenCredentialsError(Exception):
    """When invalid credentials are given when exchange access token"""


class AccessPermissionDenied(Exception):
    """Authenticated user has no access permissions"""
