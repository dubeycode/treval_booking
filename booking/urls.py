from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.travel_list_view, name='travel_list'),
    path('book/<int:travel_id>/', views.booking_create_view, name='booking_create'),
    path('booking/<str:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel/<str:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
]