# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [url(r"^authenticate/$", views.AuthenticationViewSet.as_view(), name='authenticate')]

urlpatterns += [
    url(r'^meta_info/$', views.SvcBasicViewSet.as_view({'get': 'get_meta_info'}), name='api.services.get_meta_info'),
    url(
        r'^services/$',
        views.ServiceManageViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='api.services.index',
    ),
    url(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/$',
        views.ServiceManageViewSet.as_view({'put': 'update'}),
        name='api.services.update',
    ),
    url(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/instances/(?P<instance_id>[0-9a-f-]{32,36})/$',
        views.SvcInstanceViewSet.as_view({'post': 'provision'}),
        name='api.services.instances_creation',
    ),
    url(
        r'^services/(?P<service_id>[0-9a-f-]{32,36})/client-side-instances/(?P<instance_id>[0-9a-f-]{32,36})/$',
        views.ClientSideSvcInstanceViewSet.as_view({'post': 'create'}),
        name='api.services.client_side_instances_creation',
    ),
    url(
        r'^plans/$',
        views.PlanManageViewSet.as_view({'post': 'create'}),
        name='api.plans.index',
    ),
    url(
        r'^plans/(?P<plan_id>[0-9a-f-]{32,36})/$',
        views.PlanManageViewSet.as_view({'put': 'update'}),
        name='api.plans.update',
    ),
    url(
        r'^instances/(?P<instance_id>[0-9a-f-]{32,36})/$',
        views.SvcInstanceViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}),
        name='api.services.instance',
    ),
    url(
        r'^instances/(?P<instance_id>[0-9a-f-]{32,36})/async_delete$',
        views.SvcInstanceViewSet.as_view({'delete': 'async_destroy'}),
        name='api.services.instance.async_destroy',
    ),
    url(
        r'^client-side-instances/(?P<instance_id>[0-9a-f-]{32,36})/',
        views.ClientSideSvcInstanceViewSet.as_view({'delete': 'destroy'}),
        name='api.services.client_side_instance.destroy',
    ),
    url(
        r'^instances/(?P<instance_id>[0-9a-f-]{32,36})/config/$',
        views.SvcInstanceConfigViewSet.as_view({'get': 'retrieve', 'put': 'update'}),
        name='api.services.instance_config',
    ),
]
