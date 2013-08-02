from django.contrib import admin
from weave.models import *


class ClientConfigurationAdmin(admin.ModelAdmin):
    exclude=('object_id',)



admin.site.register(WeaveManifest)
admin.site.register(WeaveMetaPublic)
admin.site.register(WeaveMetaPrivate)
admin.site.register(WeaveFlatPublicMeta)
admin.site.register(DataFilter)
admin.site.register(ClientConfiguration, ClientConfigurationAdmin)
