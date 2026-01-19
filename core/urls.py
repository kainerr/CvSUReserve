from django.urls import path
from . import views

urlpatterns = [
    # Landing Page
    path('', views.LandingPageView.as_view(), name='landing_page'),

    # Student Dashboard & Actions
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('book/', views.BookingCreateView.as_view(), name='create_booking'),
    path('success/', views.SuccessPageView.as_view(), name='success_page'),
    path('cancel-booking/<int:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),

    # Authentication
    path('signup/', views.SignupView.as_view(), name='signup'),

    # Admin Panel
    path('admin-approval/', views.AdminApprovalListView.as_view(), name='admin_approval_list'),
    path('update-booking/<int:booking_id>/<str:new_status>/', views.BookingStatusUpdateView.as_view(), name='update_booking_status'),
]