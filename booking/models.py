
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class TravelOption(models.Model):
    TRAVEL_TYPES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
    ]
    
    travel_id = models.CharField(max_length=20, unique=True)
    travel_type = models.CharField(max_length=10, choices=TRAVEL_TYPES)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_date = models.DateField()
    arrival_time = models.TimeField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['departure_date', 'departure_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(available_seats__lte=models.F('total_seats')),
                name='available_seats_lte_total_seats'
            ),
        ]
    
    def __str__(self):
        return f"{self.travel_id} - {self.source} to {self.destination}"
    
    def save(self, *args, **kwargs):
        if not self.available_seats:
            self.available_seats = self.total_seats
        super().save(*args, **kwargs)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE, related_name='bookings')
    number_of_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    
    class Meta:
        ordering = ['-booking_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(number_of_seats__gte=1) & models.Q(number_of_seats__lte=10),
                name='seats_between_1_and_10'
            ),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Auto-generate booking ID if not exists
        if not self.booking_id:
            self.booking_id = f"BK{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        # Auto-calculate total price
        if not self.total_price and self.travel_option:
            self.total_price = self.number_of_seats * self.travel_option.price
        
        super().save(*args, **kwargs)