"""
Tests for models
"""

from __future__ import unicode_literals

from django.test import TestCase

from portal.factories import CourseFactory, ModuleFactory
from portal.util import COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE


class ModelsTest(TestCase):
    """
    Tests for models.
    """

    def test_course_qualified_id(self):  # pylint: disable=no-self-use
        """
        Assert the qualified_id property
        """
        course = CourseFactory.create()
        assert course.qualified_id == "{type}_{uuid}".format(
            type=COURSE_PRODUCT_TYPE,
            uuid=course.uuid
        )

    def test_module_qualified_id(self):  # pylint: disable=no-self-use
        """
        Assert the qualified_id property
        """
        module = ModuleFactory.create()
        assert module.qualified_id == "{type}_{uuid}".format(
            type=MODULE_PRODUCT_TYPE,
            uuid=module.uuid
        )
