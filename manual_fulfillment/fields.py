"""Custom fields and widgets"""
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django import forms


class ReadOnlyWidget(forms.Widget):
    """
    Widget for rendering values as text.
    """
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            # pylint: disable=no-member
            value = self.initial
            return mark_safe("<p %s>%s</p>" % (
                flatatt(final_attrs), escape(value) or ''))

    # pylint: disable=no-self-use,unused-argument
    def _has_changed(self, initial, data):
        return False


class ReadOnlyField(forms.Field):
    """
    Form fields for rendering as plain text.

    via comments on http://lazypython.blogspot.com/2008/12/
    building-read-only-field-in-django.html
    """
    widget = ReadOnlyWidget

    def __init__(self, widget=None, label=None, initial=None, help_text=None):
        super(ReadOnlyField, self).__init__(
            self, label=label, initial=initial, help_text=help_text,
            widget=widget)
        self.widget.initial = initial

    def clean(self, value):
        return self.widget.initial
