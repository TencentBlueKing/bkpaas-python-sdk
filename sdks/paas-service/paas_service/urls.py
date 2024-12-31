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
from django.urls import re_path

from . import views

urlpatterns = [re_path(r"^authenticate/$", views.AuthenticationViewSet.as_view(), name='authenticate')]

urlpatterns += [
    re_path(r'^meta_info/$', views.SvcBasicViewSet.as_view({'get': 'get_meta_info'}), name='api.services.get_meta_info'),
    re_path(
        r'^services/$',
        views.ServiceManageViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='api.services.index',
    ),
    re_path(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/$',
        views.ServiceManageViewSet.as_view({'put': 'update'}),
        name='api.services.update',
    ),
    re_path(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/instances/(?P<instance_id>[0-9a-f-]{32,36})/$',
        views.SvcInstanceViewSet.as_view({'post': 'provision'}),
        name='api.services.instances_creation',
    ),
    re_path(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/instances/$',
        views.SvcInstanceViewSet.as_view({'get': 'retrieve_by_fields'}),
        name='api.services.instances_retrieve_by_fields',
    ),
    re_path(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/client-side-instances/(?P<instance_id>[0-9a-f-]{32,36})/$',
        views.ClientSideSvcInstanceViewSet.as_view({'post': 'create'}),
        name='api.services.client_side_instances_creation',
    ),
    re_path(
        r'^plans/$',
        views.PlanManageViewSet.as_view({'post': 'create'}),
        name='api.plans.index',
    ),
    re_path(
        r'^plans/(?P<plan_id>[0-9a-f-]{32,36})/$',
        views.PlanManageViewSet.as_view({'put': 'update'}),
        name='api.plans.update',
    ),
    re_path(
        r'^instances/(?P<instance_id>[0-9a-f-]{32,36})/$',
        views.SvcInstanceViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}),
        name='api.services.instance',
    ),
    re_path(
        r'^instances/(?P<instance_id>[0-9a-f-]{32,36})/async_delete$',
        views.SvcInstanceViewSet.as_view({'delete': 'async_destroy'}),
        name='api.services.instance.async_destroy',
    ),
    re_path(
        r'^client-side-instances/(?P<instance_id>[0-9a-f-]{32,36})/',
        views.ClientSideSvcInstanceViewSet.as_view({'delete': 'destroy'}),
        name='api.services.client_side_instance.destroy',
    ),
    re_path(
        r'^instances/(?P<instance_id>[0-9a-f-]{32,36})/config/$',
        views.SvcInstanceConfigViewSet.as_view({'get': 'retrieve', 'put': 'update'}),
        name='api.services.instance_config',
    ),
]
