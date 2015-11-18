"""
URLs for portal
"""
from django.conf.urls import url

from teachersportal.views import index_view

urlpatterns = [
    # Note: this catches all URLs
    url(r'.*', index_view, name='portal_index'),
]
