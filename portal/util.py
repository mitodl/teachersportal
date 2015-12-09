"""
Helper functions which may be generally useful.
"""

from __future__ import unicode_literals


def make_upc(product_type, external_pk):
    """
    Helper function to create unique UPC and SKU values for the database.

    Args:
        product_type (basestring):
            The name of the ProductClass associated with the Product.
        external_pk (basestring):
            An identifer string, unique within the ProductClass.
    Returns:
        basestring: A unique string id.
    """
    return "{type}_{pk}".format(type=product_type, pk=external_pk)
