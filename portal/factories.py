"""Factories for testing"""
from __future__ import unicode_literals

from django.contrib.auth.models import User
import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
import faker

from portal.models import (
    BackingInstance,
    Course,
    Module,
    Order,
    OrderLine,
    UserInfo,
)


FAKE = faker.Factory.create()


class UserInfoFactory(DjangoModelFactory):
    """Factory for UserInfo"""
    full_name = factory.LazyAttribute(lambda x: FAKE.name())
    organization = fuzzy.FuzzyText()

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = UserInfo


class UserFactory(DjangoModelFactory):
    """Factory for Users"""
    username = factory.Sequence(lambda n: "user_%d" % n)
    profile = factory.RelatedFactory(UserInfoFactory, 'user')

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = User


class BackingInstanceFactory(DjangoModelFactory):
    """Factory for BackingInstance"""
    instance_url = fuzzy.FuzzyText(prefix="http://")

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = BackingInstance


class CourseFactory(DjangoModelFactory):
    """Factory for Courses"""
    uuid = fuzzy.FuzzyText()
    title = fuzzy.FuzzyText(prefix="Course ")
    description = factory.LazyAttribute(lambda x: FAKE.text())
    live = False
    instance = factory.SubFactory(BackingInstanceFactory)

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = Course


class ModuleFactory(DjangoModelFactory):
    """Factory for Modules"""
    uuid = fuzzy.FuzzyText()
    course = factory.SubFactory(CourseFactory)
    title = fuzzy.FuzzyText(prefix="Module ")
    price_without_tax = fuzzy.FuzzyDecimal(0, 1234.5)

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = Module


class OrderFactory(DjangoModelFactory):
    """Factory for Orders"""
    subtotal = fuzzy.FuzzyDecimal(0, 1000.00)
    total_paid = fuzzy.FuzzyDecimal(0, 1000.00)
    purchaser = factory.SubFactory(UserFactory)

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = Order


class OrderLineFactory(DjangoModelFactory):
    """Factory for OrderLines"""
    order = factory.SubFactory(OrderFactory)
    price_without_tax = fuzzy.FuzzyDecimal(0, 1000.00)
    line_total = fuzzy.FuzzyDecimal(0, 1000.00)
    seats = fuzzy.FuzzyInteger(2, 60)
    module = factory.SubFactory(ModuleFactory)

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = OrderLine
