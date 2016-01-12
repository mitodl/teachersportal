"""Factories for testing"""
from django.contrib.auth.models import User
import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
import faker
from oscar.apps.catalogue.models import Product, ProductClass

from .models import Order, OrderLine, UserInfo


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


class ProductClassFactory(DjangoModelFactory):
    """Factory for Oscar ProductClass"""
    name = "Course"

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = ProductClass


class ProductFactory(DjangoModelFactory):
    """Factory for Oscar Products"""
    upc = fuzzy.FuzzyText(prefix="Course_")
    description = fuzzy.FuzzyText()
    product_class = factory.SubFactory(ProductClassFactory)
    structure = Product.PARENT
    parent = None
    title = fuzzy.FuzzyText()

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = Product


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
    product = factory.SubFactory(ProductFactory)

    class Meta:  # pylint: disable=missing-docstring,no-init,too-few-public-methods,old-style-class
        model = OrderLine
