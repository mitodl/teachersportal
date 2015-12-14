"""
URLs for portal
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from oscar.app import application as oscar

from portal.views import (
    index_view,
    ccxcon_view,
    WebhooksCCXConView,
    LoginView,
    logout_view,
    ProductListView,
)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ccxcon/', ccxcon_view, name='ccxcon-api'),
    url(r'^api/v1/webhooks/ccxcon/$', WebhooksCCXConView.as_view(), name='webhooks-ccxcon'),
    url(r'^api/v1/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/logout/$', logout_view, name='logout'),
    url(r'^api/v1/products/$', ProductListView.as_view(), name='product-list'),
]

if settings.PORTAL_OSCAR_VISIBLE:
    urlpatterns.append(
        url(r'^oscar/', include(oscar.urls))
    )

# Note: this catches all URLs so put it last
urlpatterns.append(
    url(r'.*', index_view, name='portal-index')
)
