from django.contrib import admin
from django.urls import path, include  # Import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')), # This connects your core app
]