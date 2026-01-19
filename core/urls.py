from django.urls import path
from . import views

urlpatterns = [
    # The empty path '' is now the Landing Page (Public)
    path('', views.landing_page, name='landing_page'),

    # The Dashboard is moved to 'dashboard/' (Login Required)
    path('dashboard/', views.dashboard, name='dashboard'),

    # ... keep your other URLs the same ...
    path('book/', views.create_booking, name='create_booking'),
    path('success/', views.success_page, name='success_page'),
    path('admin-approval/', views.admin_approval_list, name='admin_approval_list'),
    path('update-booking/<int:booking_id>/<str:new_status>/', views.update_booking_status, name='update_status'),
    path('signup/', views.signup, name='signup'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]