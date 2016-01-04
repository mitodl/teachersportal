"""
Utility functions for tests
"""

from __future__ import unicode_literals
import json


def as_json(resp):
    """

    Args:
        resp (HttpResponse): Response

    Returns:
        any: An object created from JSON in response.
    """
    assert resp.status_code == 200
    return json.loads(resp.content.decode('utf-8'))
