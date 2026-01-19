from django.contrib import admin
from .models import Profile, Room, Equipment, Booking, Notification

admin.site.register(Profile)
admin.site.register(Room)
admin.site.register(Equipment)
admin.site.register(Booking)
admin.site.register(Notification)