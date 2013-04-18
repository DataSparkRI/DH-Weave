from django.conf.urls.defaults import *
from weave import views
from django.conf import settings

urlpatterns = patterns('',
    url(r'^cc/(?P<config_slug>[\w-]+)$', views.get_client_config, name="get_client_config"),
    url(r'^cc-save/(?P<config_slug>[\w-]+)$', views.save_client_config, name='save_client_config'),
)

