# booking/urls.py
from django.urls import path
from . import views

app_name = 'booking'



urlpatterns = [
    # Travel list (with optional type filter)
    path('travel/', views.travel_list_view, name='travel_list_view'),
    path('travel/', views.travel_list_view, name='travel_list'),  
    path('travel/<str:travel_type>/', views.travel_list_view, name='travel_list_by_type'),

    # Bookings
    path('create/<int:travel_id>/', views.booking_create, name='booking_create'),
    path('booking/<str:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel/<str:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
]
