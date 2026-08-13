# -*- coding: utf-8 -*-
"""
We need the request object to get the user, so we'll slightly modify the
existing django.contrib.auth.get_user method. To do so we update the
auth middleware to point to our overridden method.

Calling the "patch_middleware_get_user" method somewhere like our urls.py
file takes care of hooking it in appropriately.
"""

import logging
from typing import Any

from django.contrib import auth
from django.contrib.auth import middleware, models
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def middleware_get_user(request: HttpRequest) -> Any:
    if not hasattr(request, "_cached_user"):
        request._cached_user = get_user(request)
    return request._cached_user


def _load_request_backend(request: HttpRequest, backend_path: str) -> Any:
    backend = auth.load_backend(backend_path)
    backend.request = request
    return backend


def get_user(request: HttpRequest) -> Any:
    try:
        user_id = request.session[auth.SESSION_KEY]
        backend_path = request.session[auth.BACKEND_SESSION_KEY]
        backend = _load_request_backend(request, backend_path)
        user = backend.get_user(user_id) or models.AnonymousUser()
    except KeyError:
        user = models.AnonymousUser()
    except ImportError as e:
        logger.exception(f"get an anonymous user, error: {e}")  # noqa: TRY401
        user = models.AnonymousUser()
    return user


async def aget_user(request: HttpRequest) -> Any:
    """Asynchronous counterpart of the patched :func:`get_user`."""
    try:
        user_id = await request.session.aget(auth.SESSION_KEY)
        backend_path = await request.session.aget(auth.BACKEND_SESSION_KEY)
        # SessionBase.aget() returns None for a missing key, while the synchronous
        # subscription above raises KeyError. Normalize both paths to the same behavior.
        if user_id is None or backend_path is None:
            return models.AnonymousUser()
        backend = _load_request_backend(request, backend_path)
        user = await backend.aget_user(user_id) or models.AnonymousUser()
    except KeyError:
        user = models.AnonymousUser()
    except ImportError as e:
        logger.exception(f"get an anonymous user, error: {e}")  # noqa: TRY401
        user = models.AnonymousUser()
    return user


def patch_middleware_get_user() -> None:
    middleware.get_user = middleware_get_user
    auth.get_user = get_user
    auth.aget_user = aget_user
