# -*- coding: utf-8 -*-
"""
We need the request object to get the user, so we'll slightly modify the
existing django.contrib.auth.get_user method. To do so we update the
auth middleware to point to our overridden method.

Calling the "patch_middleware_get_user" method somewhere like our urls.py
file takes care of hooking it in appropriately.
"""
import logging

from django.contrib import auth
from django.contrib.auth import middleware, models

logger = logging.getLogger(__name__)


def middleware_get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = get_user(request)
    return request._cached_user


def get_user(request):
    try:
        user_id = request.session[auth.SESSION_KEY]
        backend_path = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_path)
        backend.request = request
        user = backend.get_user(user_id) or models.AnonymousUser()
    except KeyError:
        user = models.AnonymousUser()
    except ImportError as e:
        logger.exception(f"get an anonymous user, error:{e}")
        user = models.AnonymousUser()
    return user


def patch_middleware_get_user():
    middleware.get_user = middleware_get_user
    auth.get_user = get_user
