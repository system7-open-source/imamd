"""
The chart data for the SAM reports relies on a hierarchical location structure,
and each location contains several sites. We use an MPTT tree for this.
Unfortunately the tree breaks after reloading fixtures, so we need to rebuild
it.

"""
from __future__ import print_function, unicode_literals
from django.core import management
import datetime

from django.core.management.base import BaseCommand
from locations.models import Location


class Command(BaseCommand):
    help = """rebuild MPTT tree"""

    def handle(self, *args, **options):
        # build the tree
        print('{} UTC. rebuilding tree...'.format(datetime.datetime.utcnow()))
        Location.objects.rebuild()
