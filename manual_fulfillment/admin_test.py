"""
Admin tests
"""
# pylint: disable=no-self-use
import unittest
import mock

from .models import PurchaseOrder
from .admin import PurchaseOrderAdmin


class PurchaseOrderAdminTests(unittest.TestCase):
    """
    Purchase Order Admin Tests
    """
    def test_does_not_have_delete_perms(self):
        """
        No one should have delete permissions
        """
        poa = PurchaseOrderAdmin(mock.Mock(), mock.Mock())
        assert not poa.has_delete_permission(mock.Mock())

    def test_readonly_none_for_add_view(self):
        """
        If we don't have an object, no fields should be readonly.
        """
        poa = PurchaseOrderAdmin(PurchaseOrder, mock.Mock())
        result = poa.get_readonly_fields(mock.Mock())
        assert len(result) == 0

    def test_exclude_readonly(self):
        """
        If we have an object, make everything readonly except exclude_readonly
        values.
        """
        poa = PurchaseOrderAdmin(PurchaseOrder, mock.Mock())
        result = poa.get_readonly_fields(mock.Mock(), obj=mock.Mock())
        assert 'course' in result
        assert 'ccx_id' in result
        assert 'created' in result
        assert 'info' not in result

    def test_is_processing(self):
        """Ensures we are 'processing' if ccx_id isn't set"""
        poa = PurchaseOrderAdmin(PurchaseOrder, mock.Mock())
        pobj = PurchaseOrder()
        assert poa.is_processing(pobj)
        pobj.ccx_id = 1
        assert not poa.is_processing(pobj)
