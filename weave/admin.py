from django.contrib import admin
from weave.models import *


class ClientConfigurationAdmin(admin.ModelAdmin):
    exclude=('object_id',)
    search_fields = ('name', )

class WeaveHierarchyAdmin(admin.ModelAdmin):
    list_display = ('parent_id', 'child_id')

class WeaveMetaPublicAdmin(admin.ModelAdmin):
    list_display = ('entity_id', 'meta_name', 'meta_value')
    search_fields = ['entity_id',]

class WeaveFlatPublicMetaAdmin(admin.ModelAdmin):
    list_display = ('title', 'object_id', 'weaveEntityId')
    search_fields = ['title']

admin.site.register(WeaveManifest)
admin.site.register(WeaveHierarchy, WeaveHierarchyAdmin)

admin.site.register(WeaveMetaPublic, WeaveMetaPublicAdmin)
admin.site.register(WeaveMetaPrivate)
admin.site.register(WeaveFlatPublicMeta, WeaveFlatPublicMetaAdmin)
admin.site.register(DataFilter)
admin.site.register(HubEntityIndex)
admin.site.register(ClientConfiguration, ClientConfigurationAdmin)
