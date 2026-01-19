from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# Class-Based View Imports
from django.views.generic import TemplateView, ListView, CreateView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm

# Models & Forms
from .models import Booking, Profile, Notification
from .forms import BookingForm


# ---------------------------------------------------------
# 1. LANDING PAGE & STATIC PAGES
# ---------------------------------------------------------
class LandingPageView(TemplateView):
    template_name = 'core/index.html'


class SuccessPageView(TemplateView):
    template_name = 'core/success.html'


# ---------------------------------------------------------
# 2. DASHBOARD (Read)
# ---------------------------------------------------------
class DashboardView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'core/dashboard.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Fetch bookings for the CURRENT logged-in user only
        return Booking.objects.filter(user=self.request.user).order_by('-start_time')


# ---------------------------------------------------------
# 3. CREATE BOOKING (Create)
# ---------------------------------------------------------
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'core/booking_form.html'
    success_url = reverse_lazy('success_page')

    def form_valid(self, form):
        # Attach the logged-in user before saving
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.save()
        form.save_m2m()  # Save Many-to-Many data (Equipment)
        return redirect(self.success_url)


# ---------------------------------------------------------
# 4. ADMIN APPROVAL (Read - Staff Only)
# ---------------------------------------------------------
class AdminApprovalListView(UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'core/admin_approval.html'
    context_object_name = 'bookings'

    # This replaces @staff_member_required
    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Booking.objects.filter(status='pending').order_by('start_time')


# ---------------------------------------------------------
# 5. UPDATE STATUS (Update - Staff Only)
# ---------------------------------------------------------
# Note: Since this is an action (redirect) and not a page, a standard View is best.
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