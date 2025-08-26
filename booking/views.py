from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from .models import TravelOption, Booking
from .forms import BookingForm, TravelSearchForm
import uuid

# def travel_list_view(request):
#     form = TravelSearchForm(request.GET)
#     travel_options = TravelOption.objects.filter(available_seats__gt=0)
    
#     if form.is_valid():
#         if form.cleaned_data['travel_type']:
#             travel_options = travel_options.filter(travel_type=form.cleaned_data['travel_type'])
#         if form.cleaned_data['source']:
#             travel_options = travel_options.filter(source__icontains=form.cleaned_data['source'])
#         if form.cleaned_data['destination']:
#             travel_options = travel_options.filter(destination__icontains=form.cleaned_data['destination'])
#         if form.cleaned_data['departure_date']:
#             travel_options = travel_options.filter(departure_date=form.cleaned_data['departure_date'])
    
#     paginator = Paginator(travel_options, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         'form': form,
#         'page_obj': page_obj,
#         'travel_options': page_obj.object_list
#     }
#     return render(request, 'booking/travel_list.html', context)


def travel_list_view(request):
    form = TravelSearchForm(request.GET)
    travel_options = TravelOption.objects.filter(available_seats__gt=0)
    
    if form.is_valid():
        travel_type = form.cleaned_data.get('travel_type')
        source = form.cleaned_data.get('source')
        destination = form.cleaned_data.get('destination')
        departure_date = form.cleaned_data.get('departure_date')

        if travel_type:
            travel_options = travel_options.filter(travel_type=travel_type)
        if source:
            travel_options = travel_options.filter(source__icontains=source)
        if destination:
            travel_options = travel_options.filter(destination__icontains=destination)
        if departure_date:
            travel_options = travel_options.filter(departure_date=departure_date)
    
    paginator = Paginator(travel_options, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'travel_options': page_obj.object_list
    }
    return render(request, 'booking/travel_list.html', context)


@login_required
def booking_create_view(request, travel_id):
    travel_option = get_object_or_404(TravelOption, id=travel_id, available_seats__gt=0)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, travel_option=travel_option)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)
                
                # System automatically sets these fields - NOT user input
                booking.user = request.user
                booking.travel_option = travel_option
                booking.total_price = booking.number_of_seats * travel_option.price
                booking.status = 'confirmed'
                
                # Generate unique booking ID automatically
                booking.booking_id = f"BK{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                
                # Double-check seat availability (race condition protection)
                if travel_option.available_seats < booking.number_of_seats:
                    messages.error(request, 'Sorry, not enough seats available. Please try again.')
                    return render(request, 'booking/booking_form.html', {
                        'form': form,
                        'travel_option': travel_option
                    })
                
                # Update available seats
                travel_option.available_seats -= booking.number_of_seats
                travel_option.save()
                booking.save()
                
                messages.success(
                    request, 
                    f' Booking confirmed! Your booking ID is {booking.booking_id}'
                )
                return redirect('booking:booking_detail', booking_id=booking.booking_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(travel_option=travel_option)
    
    context = {
        'form': form,
        'travel_option': travel_option
    }
    return render(request, 'booking/booking_form.html', context)

@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': booking})

@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'bookings': page_obj.object_list
    }
    return render(request, 'booking/my_bookings.html', context)

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(
        Booking, 
        booking_id=booking_id, 
        user=request.user, 
        status='confirmed'
    )
    
    # Check if booking can be cancelled (e.g., not past departure date)
    if booking.travel_option.departure_date < timezone.now().date():
        messages.error(request, 'Cannot cancel past bookings.')
        return redirect('booking:my_bookings')
    
    if request.method == 'POST':
        with transaction.atomic():
            booking.status = 'cancelled'
            booking.save()
            
            # Restore available seats
            travel_option = booking.travel_option
            travel_option.available_seats += booking.number_of_seats
            travel_option.save()
            
            messages.success(request, ' Booking cancelled successfully!')
        return redirect('booking:my_bookings')
    
    return render(request, 'booking/cancel_booking.html', {'booking': booking})

