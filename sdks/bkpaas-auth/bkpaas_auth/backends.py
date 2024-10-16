# -*- coding: utf-8 -*-
import inspect
import logging
import pickle
from typing import Dict, Optional, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.encoding import force_bytes

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.exceptions import InvalidTokenCredentialsError, ServiceError
from bkpaas_auth.core.plugins import BkTicketPlugin, BkTokenPlugin
from bkpaas_auth.core.token import (
    LoginToken,
    RequestBackend,
    TokenRequestBackend,
    create_user_from_token,
    mocked_create_user_from_token,
)
from bkpaas_auth.core.user_info import UserInfo
from bkpaas_auth.core.utils import generate_random_token
from bkpaas_auth.models import User

logger = logging.getLogger(__name__)


class UniversalAuthBackend:
    """An universal cookie auth backend.

    This backend is to be used in conjunction with the ``CookieLoginMiddleware``
    found in the middleware module of this package.
    """

    request: HttpRequest
    plugin: Union[BkTicketPlugin, BkTokenPlugin]
    request_backend: Union[RequestBackend, TokenRequestBackend]

    def __init__(self):
        self.backend_type = bkauth_settings.BACKEND_TYPE
        if self.backend_type == "bk_ticket":
            self.plugin = BkTicketPlugin()
            self.request_backend = RequestBackend()
        elif self.backend_type == "bk_token":
            self.plugin = BkTokenPlugin()
            self.request_backend = TokenRequestBackend()
        else:
            raise ImproperlyConfigured("BKAUTH_BACKEND_TYPE not set")

    def authenticate(self, request: HttpRequest, auth_credentials: Dict) -> Optional[Union[User, AnonymousUser]]:
        try:
            username = self.request_backend.request_username(**auth_credentials)
            login_token = generate_random_token()
            token = LoginToken(
                login_token=login_token,
                expires_in=bkauth_settings.LOGIN_TOKEN_EXPIRE_IN,
            )
            token.user_info = UserInfo(username=username)
            logger.debug("New login token exchanged by credentials")
        except InvalidTokenCredentialsError:
            logger.warning("authenticate error, invalid credentials given")
            return None
        except ServiceError:
            logger.warning("authenticate error, Error requesting third-party API service")
            return None

        return self.get_user_by_token(token)

    def get_user(self, user_id):
        """Get user from current session"""
        if not hasattr(self, "request"):
            return None

        # Try to get login_token from session
        token = self.get_token_from_session(self.request)
        if token:
            # Q: 为什么不调用 get_user_by_token?
            # A: 由于 get_user_by_token 需要访问远程服务, 但事实上在 authenticate 时, 用户信息已经被缓存到 token 对象中.
            #    为了减少网络开销, 所以直接调用 create_user_from_token.
            return create_user_from_token(token)
        return None

    def get_credentials(self, *args, **kwargs):
        return self.plugin.get_credentials(*args, **kwargs)

    def get_token_from_session(self, request: HttpRequest) -> Optional[LoginToken]:
        """Try getting token object from session"""
        if "user_token" not in request.session:
            return None

        try:
            user_token_pickled = force_bytes(request.session["user_token"], "latin1")
            user_token: LoginToken = pickle.loads(user_token_pickled)
        except Exception:
            logger.exception("pickle loads user_token failed")
            return None

        # token 已经过期则不返回，否则会出现 403
        if self.plugin.validate_login_token(user_token):
            return user_token
        return None

    def get_user_by_token(self, token: LoginToken) -> User:
        """Return an user object for given token object by calling Remote User Backend.

        This Method will validate token and then fetch user info from remote backend.

        :param token: token.LoginToken object
        :returns: User/AnonymousUser object
        """
        if bkauth_settings.USE_MOCKED_USER_INFO:
            user = mocked_create_user_from_token(token)
        else:
            user = token.make_user(self.request_backend.provider_type)
        return user


class DjangoAuthUserCompatibleBackend(UniversalAuthBackend):
    """兼容 django auth.User 的 backend.

    By default, the ``authenticate`` method creates ``User`` objects for usernames
    that don't already exist in the database. Subclasses can disable this behavior by setting
    the ``create_unknown_user`` attribute to ``False``.

    Note: This backend work like ``django.contrib.auth.backends.RemoteUserBackend``.
    """

    # Create a User object if not already in the database?
    create_unknown_user = True

    def authenticate(self, request: HttpRequest, auth_credentials: Dict) -> Optional[Union[User, AnonymousUser]]:
        user = super().authenticate(request, auth_credentials)
        if user:
            user = self.connect_to_django_user(user)
        return user

    def get_user(self, user_id):
        user = super().get_user(user_id)
        if user:
            user = self.connect_to_django_user(user)
        return user

    def connect_to_django_user(self, user: User):
        """Connect bkpaas_auth.User to the UserModel in the database."""
        UserModel = get_user_model()  # noqa: N806
        if self.create_unknown_user:
            db_user, created = UserModel._default_manager.get_or_create(**{UserModel.USERNAME_FIELD: user.username})
            if created:
                logger.info("User named %s is created!", user.username)
                db_user = self.configure_user(db_user=db_user, bk_user=user)
        else:
            try:
                db_user = UserModel._default_manager.get_by_natural_key(user.username)
            except UserModel.DoesNotExist:
                logger.warning("User named %s not found!", user.username)
                db_user = None

        if db_user:
            # Set those attribute to make db_user compatible with CookieLoginMiddleware
            db_user.provider_type = user.provider_type
            db_user.bkpaas_user_id = user.bkpaas_user_id
            db_user.token = user.token
        return db_user

    def configure_user(self, db_user, bk_user: User):
        """
        Configure a user after creation and return the updated user.
        """
        default_admin_superusers = getattr(settings, "DEFAULT_ADMIN_SUPERUSERS", [])
        if db_user.username in default_admin_superusers:
            db_user.is_active = True
            db_user.is_staff = True
            db_user.is_superuser = True

        db_user.email = bk_user.email or ""
        db_user.save(update_fields=["is_active", "is_staff", "is_superuser", "email"])
        return db_user


class APIGatewayAuthBackend:
    """This backend is to be used in conjunction with the ``ApiGatewayJWTUserMiddleware``
    found in the middleware module of ``apigw_manager`` package.

    """

    def authenticate_with_signature_v3(self, request, gateway_name, bk_username, verified, **credentials):
        """authenticate function with signature required by ApiGatewayJWTUserMiddleware in apigw_manager == '^3.0.0'"""
        if not verified:
            return self.make_anonymous_user(bk_username)

        return User(
            token=LoginToken("any_token", expires_in=86400),
            provider_type=self.get_provider_type(),
            username=bk_username,
        )

    def authenticate_with_signature_v1(self, request, api_name, bk_username, verified, **credentials):
        """authenticate function with signature required by ApiGatewayJWTUserMiddleware in apigw_manager == '^1.0.0'"""
        if not verified:
            return self.make_anonymous_user(bk_username)

        return User(
            token=LoginToken("any_token", expires_in=86400),
            provider_type=self.get_provider_type(),
            username=bk_username,
        )

    try:
        from apigw_manager.apigw.authentication import ApiGatewayJWTUserMiddleware

        get_user_parameters = sorted(inspect.signature(ApiGatewayJWTUserMiddleware.get_user).parameters.keys())
        v3_parameters = sorted(inspect.signature(authenticate_with_signature_v3).parameters.keys())
        if get_user_parameters == v3_parameters:
            authenticate = authenticate_with_signature_v3
        else:
            authenticate = authenticate_with_signature_v1  # type: ignore
        del get_user_parameters
        del v3_parameters
    except ImportError:
        authenticate = authenticate_with_signature_v1  # type: ignore

    def get_user(self, user_id):
        raise NotImplementedError(
            "ApiGatewayJWTUserMiddleware should be overwrite request.user, "
            "so that APIGatewayAuthBackend.get_user will never be called."
        )

    def get_provider_type(self):
        name = getattr(settings, "BKAUTH_DEFAULT_PROVIDER_TYPE", "RTX")
        return getattr(ProviderType, name)

    def make_anonymous_user(self, bk_username=None):
        user = AnonymousUser()
        user.username = bk_username
        return user
