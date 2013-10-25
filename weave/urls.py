from django.conf.urls.defaults import *
from weave import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^ds', views.weave_datasource, name='datasource'),
    url(r'^cc/(?P<config_id>[\w-]+)$', views.get_client_config, name="get_client_config"),
    url(r'^cc-save/$', views.save_client_config, name='save_client_config'),
    url(r'^embed\?file=(?P<config_path>[\w\-\./]+)$', views.embed_weave, name="embed_weave_params"),
    url(r'^embed$', views.embed_weave, name="embed_weave"),
)

