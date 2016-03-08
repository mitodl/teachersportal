"""
AppConfig
"""
from django.apps import AppConfig


class ManualFulfillmentConfig(AppConfig):
    """
    App config for this app
    """
    name = "manual_fulfillment"

    def ready(self):
        """
        Ready handler. Import signals.
        """
        import manual_fulfillment.signals
