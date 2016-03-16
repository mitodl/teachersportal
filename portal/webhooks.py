"""
Handlers for CCXCon webhooks
"""

from __future__ import unicode_literals
from six import string_types

from django.db import transaction
from rest_framework.exceptions import ValidationError

from portal.models import Course, Module, BackingInstance

# Note: reflection used for names below so be careful not to rename functions.


def course(action, payload):
    """
    Handle a CCXCon request regarding courses.

    Args:
        action: Action to take for course
        payload: Data for action
    Returns:
        HttpResponse
    """

    if action == 'update':
        try:
            title = payload['title']
            uuid = payload['external_pk']
            instance_url = payload['instance']
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))

        if not uuid:
            raise ValidationError('Invalid external_pk')
        if not isinstance(instance_url, string_types) or len(instance_url) == 0:
            raise ValidationError("Instance must be a non-empty string")

        with transaction.atomic():
            try:
                existing_course = Course.objects.get(uuid=uuid)
                if existing_course.instance.instance_url != instance_url:
                    raise ValidationError("Instance cannot be changed")
                existing_course.title = title
                existing_course.save()
            except Course.DoesNotExist:
                backing_instance, _ = BackingInstance.objects.get_or_create(
                    instance_url=instance_url
                )
                Course.objects.create(
                    uuid=uuid,
                    title=title,
                    live=False,
                    instance=backing_instance
                )
    elif action == 'delete':
        try:
            uuid = payload['external_pk']
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid value for payload")
        Course.objects.filter(uuid=uuid).delete()
    else:
        raise ValidationError("Unknown action {action}".format(action=action))


# pylint: disable=too-many-branches,too-many-statements
def module(action, payload):
    """
    Handle a CCXCon request regarding modules.

    Args:
        action: Action to take for module
        payload: Data for action
    Returns:
        HttpResponse
    """
    if action == 'update':
        try:
            title = payload['title']
            uuid = payload['external_pk']
            course_uuid = payload['course_external_pk']
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))

        if not uuid:
            raise ValidationError("Invalid external_pk")

        with transaction.atomic():
            try:
                existing_course = Course.objects.get(uuid=course_uuid)
            except Course.DoesNotExist:
                raise ValidationError("Invalid course_external_pk")

            try:
                existing_module = Module.objects.get(uuid=uuid)

                if existing_course != existing_module.course:
                    raise ValidationError("Invalid course_external_pk")

                existing_module.title = title
                existing_module.save()
            except Module.DoesNotExist:
                Module.objects.create(
                    uuid=uuid,
                    course=existing_course,
                    title=title,
                )

    elif action == 'delete':
        try:
            uuid = payload['external_pk']
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid value for payload")
        with transaction.atomic():
            Module.objects.filter(uuid=uuid).delete()
    else:
        raise ValidationError("Unknown action {action}".format(action=action))
