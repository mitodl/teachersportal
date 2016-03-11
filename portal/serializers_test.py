"""Tests for serializers"""
from __future__ import unicode_literals

from django.test import TestCase

from portal.factories import CourseFactory, ModuleFactory
from portal.serializers import (
    CourseSerializer,
    CourseSerializerReduced,
    ModuleSerializer,
)


class SerializersTest(TestCase):
    """
    Tests for serializers
    """

    def test_course_reduced_serializer(self):  # pylint: disable=no-self-use
        """Assert behavior of CourseSerializerReduced"""
        course = CourseFactory.create()
        assert dict(CourseSerializerReduced().to_representation(course)) == {
            "uuid": course.uuid,
            "title": course.title,
            "description": course.description,
            "image_url": course.image_url,
        }

    def test_course_serializer(self):  # pylint: disable=no-self-use
        """Assert behavior of CourseSerializer"""
        course = CourseFactory.create()
        module = ModuleFactory.create(course=course)
        rep = CourseSerializer(course).data
        assert isinstance(rep['instructors'], list)
        assert dict(rep) == {
            "uuid": course.uuid,
            "title": course.title,
            "author_name": course.author_name,
            "overview": course.overview,
            "description": course.description,
            "image_url": course.image_url,
            "edx_instance": course.instance.instance_url,
            "instructors": course.instructors,
            "course_id": course.course_id,
            "live": course.live,
            "modules": [
                ModuleSerializer().to_representation(module)
            ]
        }

    def test_module_serializer(self):  # pylint: disable=no-self-use
        """Assert behavior of ModuleSerializer"""
        module = ModuleFactory.create()
        assert dict(ModuleSerializer().to_representation(module)) == {
            "uuid": module.uuid,
            "title": module.title,
            "price_without_tax": float(module.price_without_tax)
        }
