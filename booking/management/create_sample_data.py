from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
import random
from booking.models import TravelOption

class Command(BaseCommand):
    help = 'Create sample travel options for testing'

    def handle(self, *args, **options):
        # Clear existing data
        TravelOption.objects.all().delete()
        
        cities = [
            'Delhi', 'Mumbai', 
            ]