"""
Model Tests
"""
# pylint: disable=no-self-use
from unittest import TestCase
from portal.models import Course
from .models import PurchaseOrder, Ammendment


class PurchaseOrderTests(TestCase):
    """
    Purchase Order Tests
    """
    def test_to_string(self):
        """
        test __str__ method
        """
        order = PurchaseOrder(title='test', seat_count=3,
                              course=Course(title="course", uuid="1"))
        assert '{}'.format(order) == "Purchase of test - 3 seats on course (1)"


class AmmendmentTests(TestCase):
    """
    Ammendment Tests
    """
    def test_to_string(self):
        """
        test __str__ method
        """
        ammendment = Ammendment(
            original_purchase_order=PurchaseOrder(title='test'))
        assert '{}'.format(ammendment) == "Ammendment to test"
