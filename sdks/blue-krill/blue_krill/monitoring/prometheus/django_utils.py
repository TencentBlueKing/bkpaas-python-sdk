# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import logging
import os
import secrets
from collections import namedtuple
from typing import Callable, Dict, Iterable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIHandler, get_path_info
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, make_wsgi_app, multiprocess

from .setups import MULTIPROC_ENV_NAME

logger = logging.getLogger(__name__)

# Validate settings
try:
    METRIC_CLIENT_TOKEN_DICT = settings.METRIC_CLIENT_TOKEN_DICT
    if not isinstance(METRIC_CLIENT_TOKEN_DICT, dict):
        raise ValueError('client token dict must be dict')
except (AttributeError, ValueError) as e:
    raise ImproperlyConfigured("METRIC_CLIENT_TOKEN_DICT is not properly configured") from e


class WSGIResponse(namedtuple('WSGIResponse', 'status data')):
    """A simple wsgi response wrapper class"""

    def write_to(self, start_response: Callable) -> Iterable:
        response_headers = [('Content-type', CONTENT_TYPE_LATEST), ('Content-Length', str(len(self.data)))]
        start_response(self.status, response_headers)
        return iter([self.data])


class PrometheusExposeHandler(WSGIHandler):
    """WSGI middleware that intercepts calls from the prometheus"""

    def __init__(self, application, exposed_path="/metrics", extra_registries=None):
        """A prometheus wsgi handler for django

        :param application: wsgi application
        :param exposed_path: path of metrics
        :param extra_registries: Extra registry objects to collect metrics from, default to None
        """
        self.application = application
        self.exposed_path = exposed_path
        extra_registries = extra_registries or []
        if os.environ.get(MULTIPROC_ENV_NAME):
            logger.info("enable prometheus using multi processes mode")

            def app(environ, start_response):
                registry = CollectorRegistry()
                multiprocess.MultiProcessCollector(registry)

                data_chunks = []

                # Combine response from 2 sources:
                #   1. the empty 'registry' object, which will load data from all files in multiproc directory
                #   2. all given extra registry objects, usually registed with custom collectors
                for r in [registry, *extra_registries]:
                    data_chunks.append(generate_latest(r))
                data = b''.join(data_chunks)

                return WSGIResponse('200 OK', data).write_to(start_response)

        else:
            logger.info("enable prometheus using single process mode")
            app = make_wsgi_app()

        self.prometheus_wsgi_app = app
        self.authenticater = HandlerAuthenticater(METRIC_CLIENT_TOKEN_DICT)
        super().__init__()

    def _should_handle(self, path):
        """Checks if the path should be handled."""
        return path.startswith(self.exposed_path)

    def __call__(self, environ, start_response):
        # Hand non-metrics requests to Django
        if not self._should_handle(get_path_info(environ)):
            return self.application(environ, start_response)

        request = self.request_class(environ)
        if self.authenticater.validate_request(request):
            return self.prometheus_wsgi_app(environ, start_response)

        return self.authenticater.generate_failed_response().write_to(start_response)


class HandlerAuthenticater:
    """Authenticater for prometheus handler"""

    key_username, key_password = 'client_id', 'user_token'

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials

    def validate_request(self, request) -> bool:
        """Validate a given request"""
        username = request.GET.get(self.key_username, '')
        password = request.GET.get(self.key_password, '')
        if not (username and password):
            return False
        return secrets.compare_digest(password, self.credentials.get(username, ''))

    def generate_failed_response(self) -> WSGIResponse:
        """Generate a failed response"""
        data = b'permission denied, no valid client_id/token provided'
        return WSGIResponse('403 FORBIDDEN', data)
