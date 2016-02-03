"""
Assign permissions
"""

from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
# pylint: skip-file


def add_permissions_to_groups(apps, schema_editor, with_create_permissions=True):
    """
    Adapted from comment in https://code.djangoproject.com/ticket/23422
    """
    Group = apps.get_model("auth", "Group")
    instructor = Group.objects.get(
        name='Instructor'
    )

    Permission = apps.get_model("auth", "Permission")
    for codename in ('edit_own_content', 'edit_own_liveness', 'edit_own_price'):
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
                return add_permissions_to_groups(
                    apps, schema_editor, with_create_permissions=False)
            else:
                raise
        instructor.permissions.add(perm)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portal', '0005_add_permissions'),
    ]

    operations = [
        migrations.RunPython(add_permissions_to_groups)
    ]
