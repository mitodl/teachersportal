"Test for gen price script"
# pylint: disable=no-self-use
from django.core.management import CommandError
from django.test import TestCase
from django.test.utils import override_settings
import pytest

from portal.models import Module
from portal.factories import ModuleFactory, CourseFactory
from .gen_prices import Command


class GenPricesTestCase(TestCase):
    "Test for gen price script"

    @override_settings(DEBUG=True)
    def test_update_modules(self):
        "Should set prices"
        ModuleFactory.create_batch(10, price_without_tax=None)
        Command().handle(course_uuid=None)

        assert not Module.objects.filter(price_without_tax__isnull=True).exists()

    @override_settings(DEBUG=False)
    def test_error_if_not_debug(self):
        "should error if not in debug environment"
        with pytest.raises(CommandError):
            Command().handle(course_uuid=None)

    @override_settings(DEBUG=True)
    def test_makes_modules(self):
        "should respect course_uuid param"
        course1 = CourseFactory.create()
        course2 = CourseFactory.create()

        ModuleFactory.create_batch(5, course=course1, price_without_tax=None)
        ModuleFactory.create_batch(5, course=course2, price_without_tax=None)
        Command().handle(course_uuid=course1.uuid)

        assert Module.objects.filter(price_without_tax__isnull=True).count() == 5
