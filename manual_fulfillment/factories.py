"""Factories for testing"""
from __future__ import unicode_literals

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from portal.factories import CourseFactory
from manual_fulfillment.models import PurchaseOrder


class PurchaseOrderFactory(DjangoModelFactory):
    """Factory for PurchaseOrder"""
    coach_email = factory.Sequence('person{0}@example.com'.format)
    seat_count = factory.Sequence(lambda n: n)
    course = factory.SubFactory(CourseFactory)
    title = fuzzy.FuzzyText()

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = PurchaseOrder
