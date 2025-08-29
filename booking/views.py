# booking/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import TravelOption, Booking
from .forms import TravelSearchForm, BookingForm

def travel_list_view(request, travel_type=None):
    # Get all travel options
    travel_options = TravelOption.objects.all()

    # Apply travel type filter if provided
    if travel_type:
        travel_options = travel_options.filter(travel_type=travel_type)

    # Other filters
    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    departure_date = request.GET.get('departure_date', '')

    if source:
        travel_options = travel_options.filter(source__icontains=source)
    if destination:
        travel_options = travel_options.filter(destination__icontains=destination)
    if departure_date:
        travel_options = travel_options.filter(departure_date=departure_date)

    # Pagination
    paginator = Paginator(travel_options, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'booking/travel_list.html', {
        'travel_options': page_obj,
        'page_obj': page_obj,
    })

@login_required
def booking_create(request, travel_id):
    travel_option = get_object_or_404(TravelOption, id=travel_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, travel_option=travel_option)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.travel_option = travel_option
            booking.save()
            
            # Update available seats
            travel_option.available_seats -= booking.number_of_seats
            travel_option.save()
            
            messages.success(request, f'Booking confirmed! ID: {booking.booking_id}')
            return redirect('booking:booking_detail', booking.booking_id)
    else:
        form = BookingForm(travel_option=travel_option)
    
    return render(request, 'booking/booking_form.html', {
        'form': form,
        'travel': travel_option,
    })

@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': booking})

@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if request.method == 'POST':
        # Return seats to travel option
        booking.travel_option.available_seats += booking.number_of_seats
        booking.travel_option.save()
        
        booking.status = 'cancelled'
        booking.save()
        
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('booking:my_bookings')
    
    return render(request, 'booking/cancel_booking.html', {'booking': booking})