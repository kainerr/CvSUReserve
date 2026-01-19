from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Choices for Profile Roles
ROLE_CHOICES = (
    ('student', 'Student'),
    ('faculty', 'Faculty'),
    ('admin', 'Admin'),
)

BOOKING_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Room(models.Model):
    name = models.CharField(max_length=100)  # e.g., "ComLab 1"
    type = models.CharField(max_length=50)  # e.g., "Laboratory"
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    total_quantity = models.IntegerField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    equipment = models.ManyToManyField(Equipment, blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')

    def clean(self):
        # Prevent Double Booking
        overlapping = Booking.objects.filter(
            room=self.room,
            status='approved',
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError(f"Room {self.room.name} is already booked for this time.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.room.name}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)