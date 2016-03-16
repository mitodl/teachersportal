"""Manual Fulfillment models"""
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from portal.models import Course


@python_2_unicode_compatible
class PurchaseOrder(models.Model):
    """
    A manual fullfillment order.
    """
    coach_email = models.EmailField()
    seat_count = models.PositiveSmallIntegerField()
    course = models.ForeignKey(Course)
    title = models.CharField(
        max_length=255, help_text="Title of the ccx in edX.")
    ccx_id = models.IntegerField(
        blank=True, null=True,
        help_text="This will be filled in by the system when it's saved.")
    info = models.TextField(
        blank=True, null=True,
        help_text="Information like purchase order number, etc")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Purchase of {0} - {1} seats on {2}'.format(
            self.title, self.seat_count, self.course)


@python_2_unicode_compatible
class Ammendment(models.Model):
    """
    A model representing edits to PurchaseOrders
    """
    original_purchase_order = models.ForeignKey(PurchaseOrder)
    new_seat_count = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        # pylint: disable=no-member
        return 'Ammendment to {}'.format(self.original_purchase_order.title)
