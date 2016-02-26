# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_groups'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ('created_at',), 'permissions': (('edit_own_content', 'Can edit descriptive content for a course and related modules'), ('edit_own_liveness', 'Can mark a course live or not live'))},
        ),
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ('created_at',), 'permissions': (('edit_own_price', 'Can edit the price of a module'),)},
        ),
    ]
