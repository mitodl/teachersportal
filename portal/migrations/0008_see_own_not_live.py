# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file


def add_see_own_not_live(apps, schema_editor, with_create_permissions=True):
    """
    Adapted from comment in https://code.djangoproject.com/ticket/23422
    """
    Group = apps.get_model("auth", "Group")
    instructor = Group.objects.get(
        name='Instructor'
    )

    Permission = apps.get_model("auth", "Permission")
    codename = 'see_own_not_live'
    try:
        perm = Permission.objects.get(
            codename=codename, content_type__app_label='portal')
    except Permission.DoesNotExist:
        if with_create_permissions:
            # Manually run create_permissions
            from django.contrib.auth.management import create_permissions
            assert not getattr(apps, 'models_module', None)
            apps.models_module = True
            create_permissions(apps, verbosity=0)
            apps.models_module = None
            return add_see_own_not_live(
                apps, schema_editor, with_create_permissions=False)
        else:
            raise
    instructor.permissions.add(perm)


def reverse_add_see_own_not_live(apps, schema_editor):
    """
    Important: the permission will get recreated in the post_migrate hook
    so the reverse migration won't work fully. However it won't be attached
    to the group or users anymore.
    """
    Permission = apps.get_model("auth", "Permission")
    Permission.objects.get(codename='see_own_not_live').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_course_owners'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ('created_at',), 'permissions': (('edit_own_content', 'Can edit descriptive content for a course and related modules'), ('edit_own_liveness', 'Can mark a course live or not live'), ('see_own_not_live', 'Can see courses which are not live'))},
        ),
        migrations.RunPython(add_see_own_not_live, reverse_add_see_own_not_live),
    ]
