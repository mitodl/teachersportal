"""Signals for Purchase Orders"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PurchaseOrder
from .tasks import create_ccx


log = logging.getLogger(__name__)


# pylint: disable=unused-argument
@receiver(post_save, sender=PurchaseOrder)
def purchase_order_post_save(instance, created, *args, **kwargs):
    """Creates a CCX when we save the purchase order request.

    If the async task doesn't get completed, we should be able to detect this
    with PurchaseOrder objects which don't have a ccx_id.
    """
    if created:
        log.debug("Sending ccx creation for purchase order %s", instance.pk)
        create_ccx.delay(instance.pk)
