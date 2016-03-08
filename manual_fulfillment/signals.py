"""Signals for Purchase Orders"""
import logging
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from portal.ccxcon_api import CCXConAPI
from .models import PurchaseOrder


log = logging.getLogger(__name__)


# pylint: disable=unused-argument
@receiver(pre_save, sender=PurchaseOrder)
def purchase_order_pre_save(instance, *args, **kwargs):
    """Creates a CCX when we save the purchase order request.

    This is necessary because this could fail, which would result in a record
    and no backing ccx. This also lets us report errors to the user in a
    meaningful way.
    """
    if not instance.pk:  # New record
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
