"""
Signals tests
"""
# pylint: disable=no-self-use
import unittest
from mock import patch
import pytest

from portal.models import Course
from .models import PurchaseOrder
from .signals import purchase_order_pre_save as pre_save


class PurchaseOrderPreSaveTests(unittest.TestCase):
    """
    Pre-save signal tests for PurchaseOrders
    """
    def setUp(self):
        self.new_po = PurchaseOrder(course=Course())

    def test_no_ccx_existing_records(self):
        """
        ccx_id shouldn't be set for existing records.
        """
        purchase_order = PurchaseOrder(pk=4, course=Course())
        pre_save(purchase_order)

        assert purchase_order.ccx_id is None

    @patch('manual_fulfillment.signals.CCXConAPI')
    def test_exception_thrown_on_fail(self, ccxcon_api):
        """
        Throws exception if the ccx call doesn't work.
        """
        ccxcon_api.return_value.create_ccx.return_value = (
            False, None, {'ccx_course_id': "foo@4"})

        with pytest.raises(RuntimeError) as exception:
            pre_save(self.new_po)

            assert 'Unable to create CCX' in str(exception.value)

    @patch('manual_fulfillment.signals.CCXConAPI')
    def test_malformed_response(self, ccxcon_api):
        """
        If CCXCon returns an unintelligible response, error.
        """
        ccxcon_api.return_value.create_ccx.return_value = (
            True, None, {'ccx_course_id': "foo"})
        with pytest.raises(RuntimeError) as exception:
            pre_save(self.new_po)

            assert 'Malformed' in str(exception.value)

    @patch('manual_fulfillment.signals.CCXConAPI')
    def test_ccx_id_on_instance(self, ccxcon_api):
        """
        If all goes well, the PurchaseOrder should have a ccx_id
        """
        ccxcon_api.return_value.create_ccx.return_value = (
            True, None, {'ccx_course_id': "foo@4"})
        assert self.new_po.ccx_id is None

        pre_save(self.new_po)

        assert self.new_po.ccx_id == 4
