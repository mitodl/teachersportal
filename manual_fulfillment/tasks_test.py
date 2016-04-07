"""Tasks tests"""
# pylint: disable=no-self-use,no-member,unused-argument
from mock import patch
import pytest
from celery.exceptions import Retry
from django.test import TestCase
from django.db.models.signals import post_save
from factory.django import mute_signals

from .factories import PurchaseOrderFactory
from .models import PurchaseOrder
from .tasks import create_ccx


@patch('manual_fulfillment.tasks.get_access_token')
@patch('manual_fulfillment.tasks.EdxApi')
class CreateCCXTests(TestCase):
    """
    Test that ccx's are created on purchase order save.
    """
    def test_ccx_id_on_instance(self, edx_api, gat):
        """
        If all goes well, the PurchaseOrder should have a ccx_id
        """
        edx_api.return_value.ccx.create.return_value = 'foo@1'
        with mute_signals(post_save):
            order = PurchaseOrderFactory.create(
                course__edx_course_id='test',
                coach_email='foo@example.com',
                seat_count=100,
                title='test title'
            )
        assert order.ccx_id is None

        create_ccx(order.pk)  # pylint: disable=no-value-for-parameter

        new_order = PurchaseOrder.objects.get(pk=order.pk)

        assert new_order.ccx_id == 1
        edx_api.return_value.ccx.create.assert_called_with(
            'test', 'foo@example.com', 100, 'test title', None)

    def test_attempts_retries(self, edx_api, gat):
        """If we fail a call, we get a retry"""
        edx_api.return_value.ccx.create.return_value = 'foo'  # missing @1
        with mute_signals(post_save):
            order = PurchaseOrderFactory.create()
        assert order.ccx_id is None

        with pytest.raises(Retry):
            create_ccx(order.pk)  # pylint: disable=no-value-for-parameter

    def test_exception_doesnt_persist(self, edx_api, gat):
        """
        If api.ccx.create raises an exception, don't set ccx_id num
        """
        edx_api.return_value.ccx.create.side_effect = Exception()
        with mute_signals(post_save):
            order = PurchaseOrderFactory.create()
            with pytest.raises(Exception):
                create_ccx(order.pk)  # pylint: disable=no-value-for-parameter

        assert PurchaseOrder.objects.get(pk=order.pk).ccx_id is None
