"""
Admin for courses and modules
"""

from __future__ import unicode_literals

from django.contrib import admin

from portal.models import Course, Module, BackingInstance


admin.site.register(Course)
admin.site.register(Module)
admin.site.register(BackingInstance)