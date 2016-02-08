# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portal', '0006_assign_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='owners',
            field=models.ManyToManyField(related_name='courses_owned', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
