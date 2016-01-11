"""
URLs for portal
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from oscar.app import application as oscar

from portal.views.activation import activate_view
from portal.views.checkout_api import checkout_view
from portal.views.login import LoginView, logout_view
from portal.views.product_api import ProductListView, ProductDetailView
from portal.views.registration import register_view
from portal.views.status import status
from portal.views.webhooks import WebhooksCCXConView
from portal.views.webpack import index_view

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/webhooks/ccxcon/$', WebhooksCCXConView.as_view(), name='webhooks-ccxcon'),
    url(r'^api/v1/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/logout/$', logout_view, name='logout'),
    url(r'^api/v1/products/$', ProductListView.as_view(), name='product-list'),
    url(r'^api/v1/products/(?P<uuid>[-\w]+)/$', ProductDetailView.as_view(), name='product-detail'),
    url(r'^api/v1/register/$', register_view, name='register'),
    url(r'^api/v1/activate/$', activate_view, name='activate'),
    url(r'^api/v1/checkout/$', checkout_view, name='checkout'),
    url(r'^status/$', status, name='status'),
]

if settings.PORTAL_OSCAR_VISIBLE:
    urlpatterns.append(
        url(r'^oscar/', include(oscar.urls))
    )

# Note: this catches all URLs so put it last
urlpatterns.append(
    url(r'.*', index_view, name='portal-index')
)
