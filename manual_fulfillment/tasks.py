"""Async Tasks"""
import logging
from edx_api.client import EdxApi

from teachersportal.celery import async
from portal.oauth import get_access_token
from portal.tasks import get_backoff
from .models import PurchaseOrder

log = logging.getLogger(__name__)


@async.task(bind=True, max_retries=5)
def create_ccx(self, purchase_order_id):
    """Create a backing CCX from a PurchaseOrder"""
    order = PurchaseOrder.objects.get(pk=purchase_order_id)  # pylint: disable=no-member
    url = order.course.instance.instance_url
    access_token = get_access_token(order.course.instance)
    api = EdxApi({'access_token': access_token}, base_url=url)

    ccx_id = api.ccx.create(
        order.course.edx_course_id,
        order.coach_email,
        order.seat_count,
        order.title,
        None
    )

    if not ccx_id:
        self.retry(countdown=get_backoff(self.request.retries))

    if '@' in ccx_id:
        order.ccx_id = int(ccx_id.split('@', 1)[1])
        order.save()
    else:
        log.info("Malformed response from ccx creation. %s", ccx_id)
        self.retry(countdown=get_backoff(self.request.retries))
