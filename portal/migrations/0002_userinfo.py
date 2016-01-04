# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('portal', '0001_populate_oscar_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('registration_token', models.TextField(null=True, blank=True)),
                ('organization', models.TextField()),
                ('full_name', models.TextField()),
            ],
        ),
    ]
