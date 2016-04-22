from django.core.management.base import BaseCommand
from core.models import LocationProgramState

class Command(BaseCommand):
    help = """Update the site state for all sites"""

    def handle(self, *args, **options):
        LocationProgramState.update_all()

        
