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
from django.contrib import admin
from paas_service.models import Plan, Service, ServiceInstance, SpecDefinition, Specification


class ServiceAdmin(admin.ModelAdmin):
    list_display = ["uuid", "display_name", "description", "is_active", "is_visible", "created", "updated"]


admin.site.register(Service, ServiceAdmin)


class PlanAdmin(admin.ModelAdmin):
    list_display = ["uuid", "name", "description", "is_active", "created", "updated"]


admin.site.register(Plan, PlanAdmin)


class ServiceInstanceAdmin(admin.ModelAdmin):
    list_display = ["uuid", "created", "updated"]


admin.site.register(ServiceInstance, ServiceInstanceAdmin)


class SpecDefinitionAdmin(admin.ModelAdmin):
    list_display = ["uuid", "display_name", "description", "created", "updated"]


admin.site.register(SpecDefinition, SpecDefinitionAdmin)


class SpecificationAdmin(admin.ModelAdmin):
    list_filter = ["definition"]
    list_display = ["uuid", "definition", "display_name", "created", "updated"]


admin.site.register(Specification, SpecificationAdmin)
