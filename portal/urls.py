"""
URLs for portal
"""
from django.conf.urls import url, include
from django.contrib import admin

from portal.views.activation import activate_view
from portal.views.checkout_api import CheckoutView
from portal.views.login import LoginView, logout_view
from portal.views.course_api import CourseListView, CourseDetailView
from portal.views.registration import register_view
from portal.views.status import status
from portal.views.webhooks import WebhooksCCXConView
from portal.views.webpack import index_view

urlpatterns = (
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/webhooks/ccxcon/$', WebhooksCCXConView.as_view(), name='webhooks-ccxcon'),
    url(r'^api/v1/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/logout/$', logout_view, name='logout'),
    url(r'^api/v1/courses/$', CourseListView.as_view(), name='course-list'),
    url(
        r'^api/v1/courses/(?P<uuid>[-\w]+)/$',
        CourseDetailView.as_view(),
        name='course-detail'
    ),
    url(r'^api/v1/register/$', register_view, name='register'),
    url(r'^api/v1/activate/$', activate_view, name='activate'),
    url(r'^api/v1/checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^status/$', status, name='status'),
    # Note: this catches all URLs so put it last
    url(r'.*', index_view, name='portal-index')
)
