from django import forms
from .models import Booking, TravelOption

from django import forms
from .models import Booking, TravelOption

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_seats']  # Only allow user to select seats
        widgets = {
            'number_of_seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,  # Maximum 10 seats per booking
                'placeholder': 'Number of seats (1-10)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.travel_option = kwargs.pop('travel_option', None)
        super().__init__(*args, **kwargs)
    
    def clean_number_of_seats(self):
        seats = self.cleaned_data['number_of_seats']
        
        if seats < 1:
            raise forms.ValidationError('Number of seats must be at least 1.')
        
        if seats > 10:
            raise forms.ValidationError('Maximum 10 seats allowed per booking.')
        
        if self.travel_option and seats > self.travel_option.available_seats:
            raise forms.ValidationError(
                f'Only {self.travel_option.available_seats} seats available.'
            )
        
        return seats

class TravelSearchForm(forms.Form):
    destination = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter destination'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )