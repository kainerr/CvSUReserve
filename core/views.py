from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone

# Class-Based View Imports
from django.views.generic import TemplateView, ListView, CreateView, View, UpdateView
from .forms import BookingForm

# Models & Forms
from .models import Booking, Profile, Notification

# UPDATES THE STATUS OF THE BOOKINGS USING TIME
def update_past_bookings():
    """
    Auto-completes bookings that have passed.
    """
    now = timezone.now()
    # Check for 'approved' bookings where the end_time is older than 'now'
    Booking.objects.filter(status='approved', end_time__lt=now).update(status='completed')

# ---------------------------------------------------------
# 1. LANDING PAGE & STATIC PAGES
# ---------------------------------------------------------
class LandingPageView(TemplateView):
    template_name = 'core/index.html'

# ---------------------------------------------------------
# 2. DASHBOARD (Read)
# ---------------------------------------------------------
class DashboardView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'core/dashboard.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # 1. Run the auto-complete check
        update_past_bookings()
        # 2. Get bookings
        return Booking.objects.filter(user=self.request.user).order_by('-start_time')

    # ADD THIS FUNCTION TO GET NOTIFICATIONS
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the last 5 notifications for this user
        context['notifications'] = Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:5]
        # (Assuming your Notification model has a 'created_at' or 'date' field)
        return context
# ---------------------------------------------------------
# 3. CREATE BOOKING (Create)
# ---------------------------------------------------------
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'core/booking_form.html'
    success_url = reverse_lazy('dashboard')  # <--- CHANGE THIS from 'success_page'

    def form_valid(self, form):
        # 1. Attach the user
        form.instance.user = self.request.user

        # 2. Add a success message (Optional but recommended)
        messages.success(self.request, "Reservation submitted successfully!")

        # 3. Let Django handle the save and redirect
        return super().form_valid(form)
# ---------------------------------------------------------
# 4. ADMIN APPROVAL (Read - Staff Only)
# ---------------------------------------------------------
class AdminApprovalListView(UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'core/admin_approval.html'
    context_object_name = 'bookings'  # This is the 'Pending' list

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # 1. TRIGGER THE CHECK (Update statuses before loading)
        update_past_bookings()

        # Return pending requests
        return Booking.objects.filter(status='pending').order_by('start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 2. Approved List (Only show UPCOMING approved bookings)
        context['approved_bookings'] = Booking.objects.filter(status='approved').order_by('start_time')

        # 3. History List (Add 'completed' here so they appear in history!)
        context['history_bookings'] = Booking.objects.filter(
            status__in=['rejected', 'cancelled', 'completed']  # <--- ADD 'completed'
        ).order_by('-start_time')

        return context

# ---------------------------------------------------------
# 5. UPDATE STATUS (Update - Staff Only)
# ---------------------------------------------------------
class BookingStatusUpdateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, booking_id, new_status):
        booking = get_object_or_404(Booking, id=booking_id)

        if new_status in ['approved', 'rejected']:
            booking.status = new_status
            booking.save()

            # Create Notification
            Notification.objects.create(
                user=booking.user,
                message=f"Your booking for {booking.room.name} has been {new_status}."
            )

        return redirect('admin_approval_list')

# ---------------------------------------------------------
# 6. SIGNUP (Create User)
# ---------------------------------------------------------
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Save the User
        user = form.save()

        # Get department from the dropdown (POST data)
        department = self.request.POST.get('department')

        # Create the Profile
        Profile.objects.create(user=user, role='student', department=department)

        # Log them in immediately
        login(self.request, user)
        return redirect(self.success_url)


# ---------------------------------------------------------
# 7. CANCEL BOOKING (Delete)
# ---------------------------------------------------------
class CancelBookingView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        # We use a custom View instead of DeleteView because we want to
        # delete on a simple link click (GET request), not a form submit.
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if booking.status == 'pending':
            booking.delete()
            messages.success(request, "Booking cancelled successfully.")
        else:
            messages.error(request, "You cannot cancel a booking that has already been processed.")

        return redirect('dashboard')

# login router for student and admin
@login_required
def login_router(request):
    if request.user.is_staff:
        # If they are staff/admin, send them to the Admin Panel
        return redirect('admin_approval_list')
    else:
        # If they are a student, send them to the Dashboard
        return redirect('dashboard')

# ---------------------------------------------------------
# 8. EDIT BOOKING (Update - Student Only, Pending Only)
# ---------------------------------------------------------
class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'core/booking_form.html' # We reuse the existing form template!
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        # SECURITY CHECK:
        # 1. Get the booking trying to be accessed
        booking = self.get_object()
        # 2. Check if the logged-in user owns it AND it is still pending
        return booking.user == self.request.user and booking.status == 'pending'

    def handle_no_permission(self):
        # If they try to hack the URL to edit an Approved booking, show an error
        messages.error(self.request, "You can only edit pending reservations.")
        return redirect('dashboard')

    def form_valid(self, form):
        # Optional: Add logic here if you need to re-validate dates
        messages.success(self.request, "Booking details updated successfully!")
        return super().form_valid(form)

# CLEAR NOTIFICATIONS FUNCTION
@login_required
def clear_notifications(request):
    # Delete all notifications for the current user
    Notification.objects.filter(user=request.user).delete()
    # Go back to the dashboard
    return redirect('dashboard')