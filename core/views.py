from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Booking  # <-- Added this import so we can fetch data
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Profile, Notification # We will use this to notify students!
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404 # <--- Verify this import exists
from django.contrib import messages

# LANDING PAGE
def landing_page(request):
    return render(request, 'core/index.html')

# 1. THE DASHBOARD (Home Page)
@login_required
def dashboard(request):
    # Fetch bookings for the CURRENT logged-in user only, ordered by newest first
    my_bookings = Booking.objects.filter(user=request.user).order_by('-start_time')

    return render(request, 'core/dashboard.html', {'bookings': my_bookings})


# 2. THE BOOKING FORM
@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # Attach the logged-in user
            booking.save()
            form.save_m2m()  # Save the equipment selection
            return redirect('success_page')
    else:
        form = BookingForm()

    return render(request, 'core/booking_form.html', {'form': form})


# 3. THE SUCCESS PAGE
def success_page(request):
    return render(request, 'core/success.html')


# 4. ADMIN DASHBOARD (For approving requests)
@staff_member_required
def admin_approval_list(request):
    # Fetch all bookings that are still 'pending'
    pending_bookings = Booking.objects.filter(status='pending').order_by('start_time')
    return render(request, 'core/admin_approval.html', {'bookings': pending_bookings})


# 5. APPROVE/REJECT ACTION
@staff_member_required
def update_booking_status(request, booking_id, new_status):
    booking = get_object_or_404(Booking, id=booking_id)

    if new_status in ['approved', 'rejected']:
        booking.status = new_status
        booking.save()

        # Create a notification for the student (Hits your Notification Objective!)
        Notification.objects.create(
            user=booking.user,
            message=f"Your booking for {booking.room.name} has been {new_status}."
        )

    return redirect('admin_approval_list')


# 6. SIGNUP
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        department = request.POST.get('department')  # Get the dropdown value

        if form.is_valid():
            user = form.save()
            # Create the Profile linked to this new User
            # We default role to 'student'
            Profile.objects.create(user=user, role='student', department=department)

            login(request, user)  # Log them in immediately
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

# 7. CANCEL BOOKING
@login_required
def cancel_booking(request, booking_id):
    # 1. Get the booking object
    # We add 'user=request.user' to ensure students can ONLY delete their OWN bookings
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # 2. Check if it is allowed to be deleted
    # (Optional: You might strictly only allow deleting 'pending' requests)
    if booking.status == 'pending':
        booking.delete()  # <--- This performs the SQL DELETE operation
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "You cannot cancel a booking that has already been processed.")

    # 3. Send them back to the dashboard
    return redirect('dashboard')