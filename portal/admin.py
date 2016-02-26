"""
Admin for courses and modules
"""

from __future__ import unicode_literals

from django.contrib import admin

from portal.models import Course, Module, BackingInstance


class ModuleInline(admin.TabularInline):
    "Module inline for editing on course admin"
    model = Module
    fields = ('title', 'price_without_tax')
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    "Course admin page"
    inlines = [
        ModuleInline
    ]


admin.site.register(Course, CourseAdmin)
admin.site.register(Module)
admin.site.register(BackingInstance)
