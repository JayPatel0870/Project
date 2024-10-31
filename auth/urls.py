# auth/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),  # Include login app URLs
    path('bill/', include('bill.urls')),    # Include bill app URLs
]
