# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0003_remove_unused_product_class"),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtotal', models.DecimalField(max_digits=20, decimal_places=2)),
                ('total_paid', models.DecimalField(max_digits=20, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purchaser', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
                ('order', models.ForeignKey(to='portal.Order')),
                ('product', models.ForeignKey(to='catalogue.Product')),
            ],
        ),
    ]
