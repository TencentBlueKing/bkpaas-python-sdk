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
