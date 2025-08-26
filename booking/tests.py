from django.test import TestCase,Client

# Create your tests here.
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
from .models import TravelOption, Booking

class TravelBookingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='FL001',
            travel_type='flight',
            source='Delhi',
            destination='Mumbai',
            departure_date=date.today() + timedelta(days=1),
            departure_time=time(10, 30),
            arrival_date=date.today() + timedelta(days=1),
            arrival_time=time(12, 30),
            price=Decimal('5000.00'),
            total_seats=100,
            available_seats=100
        )

    def test_travel_option_creation(self):
        """Test travel option model creation"""
        self.assertEqual(self.travel_option.travel_id, 'FL001')
        self.assertEqual(self.travel_option.available_seats, 100)
        self.assertEqual(str(self.travel_option), 'FL001 - Delhi to Mumbai')

    def test_booking_creation(self):
        """Test booking model creation"""
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2
        )
        self.assertEqual(booking.number_of_seats, 2)
        self.assertEqual(booking.total_price, Decimal('10000.00'))
        self.assertEqual(booking.status, 'confirmed')

    def test_travel_list_view(self):
        """Test travel options listing"""
        response = self.client.get(reverse('booking:travel_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FL001')

    def test_booking_requires_login(self):
        """Test that booking requires authentication"""
        response = self.client.get(
            reverse('booking:booking_create', args=[self.travel_option.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_successful_booking(self):
        """Test successful booking process"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('booking:booking_create', args=[self.travel_option.id]),
            {'number_of_seats': 2}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        
        # Check booking was created
        booking = Booking.objects.get(user=self.user)
        self.assertEqual(booking.number_of_seats, 2)
        
        # Check available seats decreased
        updated_travel = TravelOption.objects.get(id=self.travel_option.id)
        self.assertEqual(updated_travel.available_seats, 98)

    def test_booking_validation(self):
        """Test booking validation for available seats"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('booking:booking_create', args=[self.travel_option.id]),
            {'number_of_seats': 150}  # More than available
        )
        self.assertEqual(response.status_code, 200)  # Stay on form with errors
        self.assertContains(response, 'Only 100 seats available')

    def test_booking_cancellation(self):
        """Test booking cancellation"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create booking
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2
        )
        
        # Update available seats
        self.travel_option.available_seats -= 2
        self.travel_option.save()
        
        # Cancel booking
        response = self.client.post(
            reverse('booking:cancel_booking', args=[booking.booking_id])
        )
        self.assertEqual(response.status_code, 302)
        
        # Check booking status
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        
        # Check seats restored
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, 100)