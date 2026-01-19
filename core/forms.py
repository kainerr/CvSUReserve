from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # We don't show 'user' or 'status' because the system handles those automatically
        fields = ['room', 'equipment', 'start_time', 'end_time', 'purpose']

        # This adds calendar widgets to the date fields
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'equipment': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }