"""
Signals tests
"""
# pylint: disable=no-self-use
import unittest
from mock import patch

from portal.models import Course
from .models import PurchaseOrder
from .signals import purchase_order_post_save as post_save


@patch('manual_fulfillment.signals.create_ccx')
class PurchaseOrderPostSaveTests(unittest.TestCase):
    """
    Pre-save signal tests for PurchaseOrders
    """
    def setUp(self):
        self.new_po = PurchaseOrder(course=Course())

    def test_creates_ccx_on_create(self, create_task):
        """When we create the PurchaseOrder, create the CCX async"""
        post_save(PurchaseOrder(pk=1), created=True)
        create_task.delay.assert_called_with(1)

    def test_no_create_on_update(self, create_task):
        """Don't recreate the CCX if it's an update."""
        post_save(PurchaseOrder(pk=1), created=False)
        assert not create_task.delay.called
