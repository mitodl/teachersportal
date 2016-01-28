"""
Tests for models
"""

from __future__ import unicode_literals

from django.test import TestCase

from portal.factories import (
    CourseFactory,
    ModuleFactory,
    BackingInstanceFactory,
)


class ModelsTests(TestCase):
    """
    Models tests
    """

    def test_course_str(self):  # pylint: disable=no-self-use
        """
        Assert str(Course)
        """
        course = CourseFactory.create()
        expected = "{title} ({uuid})".format(title=course.title, uuid=course.uuid)
        assert str(course) == expected

    def test_module_str(self):  # pylint: disable=no-self-use
        """
        Assert str(Module)
        """
        module = ModuleFactory.create()
        expected = "{title} ({uuid})".format(title=module.title, uuid=module.uuid)
        assert str(module) == expected

    def test_backinginstance_str(self):  # pylint: disable=no-self-use
        """
        Assert str(BackingInstance)
        """
        instance = BackingInstanceFactory.create()
        expected = instance.instance_url
        assert str(instance) == expected
