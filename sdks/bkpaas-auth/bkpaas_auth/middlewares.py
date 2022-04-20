# -*- coding: utf-8 -*-
import logging
import pickle
import time
from typing import Dict

from bkpaas_auth.backends import UniversalAuthBackend
from django.conf import settings
from django.contrib import auth
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_text

logger = logging.getLogger(__name__)


class CookieLoginMiddleware(MiddlewareMixin):
    """Call auth.login when user credential cookies changes"""

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The CookieLoginMiddleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'bkpaas_auth.middlewares.CookieLoginMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")

        backend = UniversalAuthBackend()
        credentials = backend.get_credentials(request)

        # No credentials, call logout
        if not credentials:
            auth.logout(request)
            return self.get_response(request)

        if self.should_authenticate(request, backend, credentials):
            self.authenticate_and_login(request, credentials)

        return self.get_response(request)

    def should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: Dict[str, str]
    ) -> bool:
        """Decide whether to re-authenticate current credentials or not"""
        # Force re-login if credentials is different from last time
        credentials_been_modified = credentials != request.session.get('auth_credentials', {})
        if credentials_been_modified:
            return True

        # Force re-login if token is empty or obsolete
        token = backend.get_token_from_session(request)
        return token is None

    def authenticate_and_login(self, request: HttpRequest, credentials: Dict[str, str]):
        """Authenticate given credentials and do login(or logout if credentials is invalid)

        :params request: Current request object
        :params credentials: user credentials, such as uin/skey pair
        """
        logger.debug('Authenticating credentials...')
        user = auth.authenticate(request=request, auth_credentials=credentials)
        if user is None or not user.is_authenticated:
            logger.info('Authentication failed, logout.')
            auth.logout(request)
            return

        backend = auth.load_backend(user.backend)
        if not isinstance(backend, UniversalAuthBackend):
            logger.info("User is not validate by UniversalAuthBackend, skip login processes.")
            return

        logger.debug('Authentication finished, username: %s', user.username)
        request.session['provider_type'] = user.provider_type.value
        request.session['bkpaas_user_id'] = user.bkpaas_user_id
        request.session['bkpaas_authenticated_at'] = time.time()
        request.session['auth_credentials'] = credentials
        # python3 compatibility
        request.session['user_token'] = force_text(pickle.dumps(user.token), 'latin1')

        # Calling `auth.login` will rotate CSRF token and modify user session, only do this when the authenticated
        # user was different with the user stored in session. Otherwise CSRF token validation may fail due to the
        # rotation.
        if getattr(request, "user", None) != user:
            auth.login(request, user)
