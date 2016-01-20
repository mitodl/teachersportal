# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.TextField()),
                ('title', models.TextField()),
                ('description', models.TextField(null=True, blank=True)),
                ('live', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.TextField()),
                ('title', models.TextField()),
                ('price_without_tax', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(to='portal.Course')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtotal', models.DecimalField(max_digits=20, decimal_places=2)),
                ('total_paid', models.DecimalField(max_digits=20, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seats', models.IntegerField()),
                ('price_without_tax', models.DecimalField(max_digits=20, decimal_places=2)),
                ('line_total', models.DecimalField(max_digits=20, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='portal.Module')),
                ('order', models.ForeignKey(to='portal.Order')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('registration_token', models.TextField(null=True, blank=True)),
                ('organization', models.TextField()),
                ('full_name', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='purchaser',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
