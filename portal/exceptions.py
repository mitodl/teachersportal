"""
Exceptions used in the Teacher's Portal
"""

from __future__ import unicode_literals


class ProductException(Exception):
    """
    Exception raised when our own validation of oscar's Product model fails.
    This is not a ValidationError because this should only be raised when data
    integrity has failed (resulting in a 500).
    """
