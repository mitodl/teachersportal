# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file

EXAMPLE_URL = "http://example.com/"

def add_default_backinginstance(apps, schema_editor):
    BackingInstance = apps.get_model("portal", "BackingInstance")
    BackingInstance.objects.create(instance_url=EXAMPLE_URL)


def reverse_add_default_backinginstance(apps, schema_editor):
    BackingInstance = apps.get_model('portal', 'BackingInstance')
    BackingInstance.objects.filter(instance_url=EXAMPLE_URL).all().delete()


def populate_default_backinginstance(apps, schema_editor):
    BackingInstance = apps.get_model("portal", "BackingInstance")
    Course = apps.get_model("portal", "Course")
    instance = BackingInstance.objects.get(instance_url=EXAMPLE_URL)
    # This assumes we never have too many objects where we need a bulk insert
    for course in Course.objects.all():
        course.instance = instance
        course.save()


def reverse_populate_default_backinginstance(apps, schema_editor):
    BackingInstance = apps.get_model("portal", "BackingInstance")
    BackingInstance.objects.get(instance_url=EXAMPLE_URL).course_set.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackingInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance_url', models.TextField()),
            ],
        ),
        migrations.RunPython(add_default_backinginstance, reverse_add_default_backinginstance),
        migrations.AddField(
            model_name='course',
            name='instance',
            field=models.ForeignKey(to='portal.BackingInstance', null=True),
        ),
        migrations.RunPython(populate_default_backinginstance, reverse_populate_default_backinginstance),
        migrations.AlterField(
            model_name='course',
            name='instance',
            field=models.ForeignKey(to='portal.BackingInstance')
        )
    ]
