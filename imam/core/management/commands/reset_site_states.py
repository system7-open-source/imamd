from django.core.management.base import BaseCommand
from core.models import LocationProgramState

class Command(BaseCommand):
    help = """Reset the sites for all current states using all information available"""

    def handle(self, *args, **options):
        LocationProgramState.reset_all()

        
