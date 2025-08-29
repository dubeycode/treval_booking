# booking/forms.py
from django import forms
from .models import Booking, TravelOption

class TravelSearchForm(forms.Form):
    travel_type = forms.ChoiceField(
        choices=[('', 'All Types')] + TravelOption.TRAVEL_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    source = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter source city'
        })
    )
    destination = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter destination'
        })
    )
    departure_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date'
        })
    )

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_seats']
        widgets = {
            'number_of_seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
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