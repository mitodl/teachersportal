"""
Admin interface
"""
from django.contrib import admin

from .models import PurchaseOrder


class PurchaseOrderAdmin(admin.ModelAdmin):
    """ModelAdmin for PurchaseOrders"""
    exclude = ('ccx_id',)
    list_display = ('__str__', 'course', 'coach_email', 'seat_count', 'created')
    list_filter = ('created',)

    exclude_readonly = ('info',)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        """
        If we're looking at the detail view, just show a read-only
        representation unless we're creating one for the first time.

        Still allow people to edit some fields (like info).
        """
        if obj:
            # pylint: disable=protected-access
            return set(self.model._meta.get_all_field_names()) - set(
                self.exclude_readonly)
        return super(PurchaseOrderAdmin, self).get_readonly_fields(request, obj)


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
