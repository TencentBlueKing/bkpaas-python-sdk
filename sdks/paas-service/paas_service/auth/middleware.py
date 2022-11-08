# -*- coding: utf-8 -*-
"""auth middlewares"""
import logging
from typing import Optional

from .backends import AuthFailedError, JWTClientAuthenticater

logger = logging.getLogger(__name__)


class VerifiedClientMiddleware(object):
    """This middleware will inject request.verifed_client if current request has a valid
    signed JWT token in request headers
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_token(request) -> Optional[str]:
        """Get token from request, return None if no token can be found"""
        auth_header_val = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header_val:
            return None

        try:
            prefix, token = auth_header_val.split(None, 1)
        except ValueError:
            logger.warning('Invalid authorization header value')
            return None

        return token

    def __call__(self, request):
        token = self.get_token(request)
        request.client = None
        if token:
            try:
                ret = JWTClientAuthenticater().authenticate(token=token)
                request.client = ret.client
            except AuthFailedError:
                pass

        response = self.get_response(request)
        return response
