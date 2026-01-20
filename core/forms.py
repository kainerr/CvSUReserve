# core/forms.py

from django import forms
from .models import Booking
from django.core.exceptions import ValidationError

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'start_time', 'end_time', 'purpose', 'equipment']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'equipment': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            # 1. Check if End Time is before Start Time
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")

            # 2. Check for Overlapping Bookings
            # We look for bookings for the SAME room that overlap with the requested time.
            # (start < request_end) AND (end > request_start)
            overlapping_bookings = Booking.objects.filter(
                room=room,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(status__in=['rejected', 'cancelled']) # Ignore rejected/cancelled ones

            # If we are editing an existing booking, exclude itself from the check
            if self.instance.pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)

            if overlapping_bookings.exists():
                raise ValidationError(f"Sorry, {room.name} is already booked for this time slot.")

        return cleaned_data