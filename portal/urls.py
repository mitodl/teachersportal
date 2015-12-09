"""
URLs for portal
"""
from django.conf.urls import url, include
from django.contrib import admin
from oscarapi.app import application as oscar_api

from portal.views import index_view, ccxcon_view, WebhooksCCXConView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oscarapi/', include(oscar_api.urls)),
    url(r'^ccxcon/', ccxcon_view, name='ccxcon-api'),
    url(r'^api/v1/webhooks/ccxcon/$', WebhooksCCXConView.as_view(), name='webhooks-ccxcon'),
    # Note: this catches all URLs so put it last
    url(r'.*', index_view, name='portal-index'),
]
