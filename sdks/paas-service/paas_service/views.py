# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
import json
import logging
from contextlib import contextmanager

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.decorators import method_decorator
from django.views import View
from paas_service import __version__, serializers
from paas_service.auth.backends import InstanceAuthBackend, InstanceAuthFailed
from paas_service.auth.decorator import verified_client_required, verified_client_role_require
from paas_service.base_vendor import ArgumentInvalidError, InstanceData, OperationFailed, get_provider_cls
from paas_service.mixins import LoginRequiredMixin
from paas_service.models import Plan, Service, ServiceInstance, ServiceInstanceConfig
from paas_service.utils import parse_redirect_params
from rest_framework import status, viewsets
from rest_framework.response import Response

logger = logging.getLogger(__name__)


m_verified_client_required = method_decorator(verified_client_required)


class AuthenticationViewSet(LoginRequiredMixin, View):
    """View for authentication"""

    def get(self, request):
        """Accepts and validates a JWT token parameter in GET string, will redirect to the index
        page of the instance after a successfully validation
        """
        try:
            instance = InstanceAuthBackend().invoke(request)
        except InstanceAuthFailed as e:
            logger.error(f'unable to authenticate current request: {e}')
            raise Http404

        view_name, params = parse_redirect_params(
            request.GET.get("redirect_url", None), instance_id=str(instance.uuid)
        )
        return redirect(reverse(view_name, kwargs=params))


class SvcBasicViewSet(viewsets.ViewSet):
    """Basic views for services"""

    def get_meta_info(self, request):
        """Return service meta info"""
        return Response({'version': __version__})


class ServiceManageViewSet(viewsets.ViewSet):
    """Manage view for services"""

    @verified_client_role_require('internal_platform')
    def list(self, request):
        services = Service.objects.filter(is_active=True).prefetch_related('plans')
        slz = serializers.ServiceListSLZ(services, many=True)
        return Response(slz.data)

    @verified_client_role_require('internal_platform')
    def update(self, request, service_id):
        service = get_object_or_404(Service, pk=service_id)
        slz = serializers.ServiceUpsertSLZ(data=request.data, instance=service, partial=True)
        slz.is_valid(raise_exception=True)
        slz.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @verified_client_role_require('internal_platform')
    def create(self, request):
        slz = serializers.ServiceUpsertSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        slz.save()
        return Response(status=status.HTTP_201_CREATED)

    @verified_client_role_require('internal_platform')
    def destroy(self, request, service_id):
        service = get_object_or_404(Service, pk=service_id)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlanManageViewSet(viewsets.ViewSet):
    """Manage view for Plan"""

    @verified_client_role_require('internal_platform')
    def create(self, request):
        slz = serializers.PlanUpsertSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        slz.save()
        return Response(status=status.HTTP_201_CREATED)

    @verified_client_role_require('internal_platform')
    def update(self, request, plan_id):
        plan = get_object_or_404(Plan, pk=plan_id)
        slz = serializers.PlanUpsertSLZ(data=request.data, instance=plan, partial=True)
        slz.is_valid(raise_exception=True)
        slz.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @verified_client_role_require('internal_platform')
    def destroy(self, request, plan_id):
        plan = get_object_or_404(Plan, pk=plan_id)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SvcInstanceViewSet(viewsets.ViewSet):
    """Instance view set"""

    @verified_client_role_require('internal_platform')
    def provision(self, request, service_id, instance_id):
        """Provision a new instance

        an example request data:

            {
                "plan_id": "f8ad12f2-4dd5-4871-8e31-9a1f9f3795a2",
                "params": {
                    "username": "example-bucket"
                }
            }

        """
        if ServiceInstance.objects.filter(pk=instance_id):
            # TODO: Replace with standard error code
            return Response(data={'detail': f'instance {instance_id} already exists'}, status=400)

        service = get_object_or_404(Service, pk=service_id)
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response(data={'detail': 'plan_id is missing'}, status=400)

        provider_cls = get_provider_cls()
        plan = get_object_or_404(Plan, service=service, pk=plan_id)

        plan_config = json.loads(plan.config)
        params = request.data.get('params', {})
        with wrap_provider_action_exc('create instance') as ret:
            instance_data = provider_cls(**plan_config).create(params=params)

        if ret.has_error:
            return ret.response

        service_instance = ServiceInstance.objects.create(
            pk=instance_id,
            service=service,
            plan=plan,
            config=instance_data.config,
            credentials=json.dumps(instance_data.credentials),
        )
        service_instance.prerender(request)
        return Response(serializers.ServiceInstanceSLZ(service_instance).data, status=201)

    @m_verified_client_required
    def retrieve(self, request, instance_id):
        """Retrieve an instance"""
        slz = serializers.ServiceInstanceQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance = get_object_or_404(ServiceInstance, pk=instance_id, to_be_deleted=data.get("to_be_deleted", False))
        instance.prerender(request)
        return Response(serializers.ServiceInstanceSLZ(instance).data)

    @m_verified_client_required
    def retrieve_by_fields(self, request, service_id):
        """Retrieve an instance by fields"""
        qs = ServiceInstance.objects.filter(service__uuid=service_id)
        # 由于 name 在 credentials 加密字段中， 所以不能直接使用 filter 过滤
        # 只能遍历所有 ServiceInstance 来查找
        name = request.GET.get("name")
        for instance in qs:
            credentials = instance.get_credentials()
            if credentials.get('name') == name:
                instance.prerender(request)
                return Response(serializers.ServiceInstanceSLZ(instance).data)
        return Response(status=404)

    @verified_client_role_require('internal_platform')
    def update(self, request, instance_id):
        return Response(data={'detail': 'not available'}, status=400)

    @verified_client_role_require('internal_platform')
    def destroy(self, request, instance_id):
        """Destroy an instance"""
        instance = get_object_or_404(ServiceInstance, pk=instance_id)
        provider_cls = get_provider_cls()
        instance_data = InstanceData(
            credentials=json.loads(instance.credentials),
            config=instance.config,
        )
        plan_config = json.loads(instance.plan.config)

        with wrap_provider_action_exc(f'remove instance {instance.uuid}') as ret:
            provider_cls(**plan_config).delete(instance_data)

        if ret.has_error:
            return ret.response

        instance.delete()
        return Response(status=204)

    @verified_client_role_require('internal_platform')
    def async_destroy(self, request, instance_id):
        """Destroy an instance async, record it into db"""
        instance = get_object_or_404(ServiceInstance, pk=instance_id)

        try:
            instance.to_be_deleted = True
            instance.save(update_fields=["to_be_deleted"])
        except Exception as e:
            logger.exception("mark instance need to delete failed")
            return Response(data={'detail': f'unable to mark instance<{instance_id}> to delete: {e}'})

        return Response(status=204)


class ClientSideSvcInstanceViewSet(viewsets.ViewSet):
    @verified_client_role_require('internal_platform')
    def create(self, request, service_id, instance_id):
        """create service instance with the existing config and credentials.

        an example request data:
            {
                "config": {
                    ...
                },
                "credentials": {
                    ...
                }
            }

        """
        if ServiceInstance.objects.filter(pk=instance_id):
            # TODO: Replace with standard error code
            return Response(data={'detail': f'instance {instance_id} already exists'}, status=400)

        slz = serializers.ServiceInstanceBinderSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        config = data["config"]
        credentials = data["credentials"]
        service = get_object_or_404(Service, pk=service_id)
        service_instance = ServiceInstance.objects.create(
            pk=instance_id,
            service=service,
            plan=None,
            config=config,
            credentials=json.dumps(credentials),
        )
        service_instance.prerender(request)
        return Response(serializers.ServiceInstanceSLZ(service_instance).data, status=201)

    @verified_client_role_require('internal_platform')
    def destroy(self, request, instance_id):
        """Unbind the instance without reclaiming resources."""
        instance = get_object_or_404(ServiceInstance, pk=instance_id)
        if not instance.from_client_side:
            return Response(data={'detail': f'instance {instance_id} is not a client-side instance'}, status=400)
        instance.delete()
        return Response(status=204)


class SvcInstanceConfigViewSet(viewsets.ViewSet):
    """InstanceConfig view"""

    @verified_client_role_require('internal_platform')
    def retrieve(self, request, instance_id):
        """Retrieve an instance's config"""
        instance = get_object_or_404(ServiceInstance, pk=instance_id)
        config, _ = ServiceInstanceConfig.objects.get_or_create(instance=instance)
        if not config.was_initialized():
            return Response(data={'detail': 'config was not initialized yet'}, status=400)

        slz = serializers.InstanceConfigSLZ(config)
        return Response(slz.data)

    @verified_client_role_require('internal_platform')
    def update(self, request, instance_id):
        """Update an instance's config"""
        instance = get_object_or_404(ServiceInstance, pk=instance_id)
        slz = serializers.InstanceConfigSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        # Update config
        config, _ = ServiceInstanceConfig.objects.update_or_create(
            instance=instance, defaults={'paas_app_info': slz.validated_data['paas_app_info']}
        )
        resp_slz = serializers.InstanceConfigSLZ(config)
        return Response(resp_slz.data)


@contextmanager
def wrap_provider_action_exc(action_name: str):
    """use this as a context manager to transform provider operation exceptions into user
    friendly error messages
    """

    class OpResult:
        def __init__(self):
            self.response = None
            self.has_error = False

        def set_ok(self):
            self.has_error = False

        def set_fail_with_resp(self, resp: HttpResponse):
            self.has_error = True
            self.response = resp

    ret = OpResult()
    try:
        yield ret
    except ArgumentInvalidError as e:
        logger.exception(f'argument error when {action_name}')
        ret.set_fail_with_resp(Response(data={'detail': f'params error: {e}'}, status=400))
    except OperationFailed as e:
        logger.exception(f'operation failed while {action_name}')
        ret.set_fail_with_resp(Response(data={'detail': f'operation failed: {e}'}, status=500))
    except Exception:
        logger.exception(f'error while {action_name}')
        ret.set_fail_with_resp(Response(data={'detail': f'unable to {action_name}'}, status=500))
    else:
        ret.set_ok()
