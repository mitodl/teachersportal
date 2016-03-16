"""
Admin interface
"""
from django.contrib import admin

from .models import PurchaseOrder, Ammendment
from .forms import AmmendmentForm


class AmmendmentInline(admin.StackedInline):
    """Inline for Ammendments"""
    model = Ammendment
    form = AmmendmentForm
    extra = 0
    can_delete = False
    ordering = ('created',)
    fields = ('new_seat_count', 'created',)
    readonly_fields = ('created',)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        """
        Number of available ammendments is 1 more than we currently have.
        """
        if not obj:
            return None
        return obj.ammendment_set.count() + 1


class PurchaseOrderAdmin(admin.ModelAdmin):
    """ModelAdmin for PurchaseOrders"""
    exclude = ('ccx_id',)
    list_display = ('__str__', 'course', 'coach_email', 'seat_count',
                    'created')
    list_filter = ('created',)
    inlines = [
        AmmendmentInline
    ]

    exclude_readonly = ('info', 'ammendment',)

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
        return super(PurchaseOrderAdmin, self).get_readonly_fields(
            request, obj)


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
