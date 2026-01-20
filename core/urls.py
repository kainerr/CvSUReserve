from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Landing Page
    path('', views.LandingPageView.as_view(), name='landing_page'),

    # Student Dashboard & Actions
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('book/', views.BookingCreateView.as_view(), name='create_booking'),
    path('cancel-booking/<int:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),

    # Authentication
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login-redirect/', views.login_router, name='login_redirect'),
    path('logout/', LogoutView.as_view(next_page='landing_page'), name='logout'),

    # Admin Panel
    path('admin-approval/', views.AdminApprovalListView.as_view(), name='admin_approval_list'),
    path('update-booking/<int:booking_id>/<str:new_status>/', views.BookingStatusUpdateView.as_view(), name='update_booking_status'),
    path('edit-booking/<int:pk>/', views.BookingUpdateView.as_view(), name='edit_booking'),
]