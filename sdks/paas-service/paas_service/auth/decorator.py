# -*- coding: utf-8 -*-
import logging
from collections.abc import Mapping
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


def instance_authorized_require(func):
    """Decorator for view methods which use an "instance_id" as first argument,
    will check session to see if instance_id requested has been authorized via
    backends.
    """

    @wraps(func)
    def wrapper(request, instance_id, *args, **kwargs):
        authorized_instances = request.session.get('authorized_instances', {})
        if not isinstance(authorized_instances, Mapping):
            logger.error('authorized_instances type error')
            return HttpResponseServerError('internal server error, please try again')

        # Check if instance has been authorized
        if instance_id not in authorized_instances:
            raise PermissionDenied()

        return func(request, instance_id, *args, **kwargs)

    return wrapper


def verified_client_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        client = getattr(request, 'client', None)
        if client and client.is_verified():
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    return wrapper


def verified_client_role_require(role_name):
    """check if role exist with covering features of the above decorator"""

    @method_decorator
    def _wrapper(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            client = getattr(request, 'client', None)
            if client and client.is_verified() and role_name == client.role:
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied()

        return _wrapped

    return _wrapper
