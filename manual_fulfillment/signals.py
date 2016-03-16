"""Signals for Purchase Orders"""
import logging
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from portal.ccxcon_api import CCXConAPI
from .models import PurchaseOrder, Ammendment


log = logging.getLogger(__name__)


# pylint: disable=unused-argument
@receiver(pre_save, sender=PurchaseOrder)
def purchase_order_pre_save(instance, *args, **kwargs):
    """Creates a CCX when we save the purchase order request.

    This is necessary because this could fail, which would result in a record
    and no backing ccx. This also lets us report errors to the user in a
    meaningful way.
    """
    if instance.pk:  # Existing record
        return

    api = CCXConAPI(
        settings.CCXCON_API,
        settings.CCXCON_OAUTH_CLIENT_ID,
        settings.CCXCON_OAUTH_CLIENT_SECRET,
    )
    works, _, content = api.create_ccx(
        instance.course.uuid,
        instance.coach_email,
        instance.seat_count,
        instance.title,
        None
    )

    if not works:
        raise RuntimeError("Unable to create CCX. {}".format(content))

    if 'ccx_course_id' in content and '@' in content['ccx_course_id']:
        instance.ccx_id = int(content['ccx_course_id'].split('@')[1])
    else:
        log.info("Malformed response from ccx creation. %s", content)
        raise RuntimeError("Malformed response from CCX Creation")


@receiver(pre_save, sender=Ammendment)
def ammendment_pre_save(instance, *args, **kwargs):
    """
    Updates the CCX to reflect new seat counts.
    """
    if instance.pk:  # Existing record
        return

    ccx_id = instance.original_purchase_order.ccx_id
    if not ccx_id:
        raise AttributeError(
            "Cannot edit seats on Purchase Orders without a ccx_id")

    api = CCXConAPI(
        settings.CCXCON_API,
        settings.CCXCON_OAUTH_CLIENT_ID,
        settings.CCXCON_OAUTH_CLIENT_SECRET,
    )

    api.update_ccx_seats(
        instance.original_purchase_order.course.uuid,
        instance.original_purchase_order.ccx_id,
        instance.new_seat_count,
    )
