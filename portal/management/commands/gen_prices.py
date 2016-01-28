"""
Generates fake prices for data.
"""

from random import randint
from django.conf import settings
from django.core.management import BaseCommand, CommandError

from portal.models import Module


class Command(BaseCommand):
    """
    Generates fake prices.
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--course-uuid',
            dest='course_uuid',
            help='Optional course id to generate prices for',
        )

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError("Not altering prices in non-debug environment.")

        lookup = {
            'price_without_tax__isnull': True
        }
        if kwargs['course_uuid']:
            lookup['course__uuid'] = kwargs['course_uuid']
        total = 0
        for module in Module.objects.filter(**lookup):
            module.price_without_tax = randint(1, 15)
            module.save()
            total += 1

        self.stdout.write("Updated prices on {} modules".format(total))
