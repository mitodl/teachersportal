"""
Custom forms.
"""
from django.forms import ModelForm

from .models import Ammendment
from .fields import ReadOnlyField


# pylint: disable=too-few-public-methods
class AmmendmentForm(ModelForm):
    """
    Form for editing Ammendments.
    """
    class Meta:  # pylint: disable=missing-docstring
        model = Ammendment
        fields = ('new_seat_count',)

    def __init__(self, *args, **kwargs):
        super(AmmendmentForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['new_seat_count'] = ReadOnlyField(
                initial=instance.new_seat_count)
