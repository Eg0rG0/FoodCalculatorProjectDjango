from django.contrib import admin
from django.urls import path, include
from BZYCalculator.views import page_not_found
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('BZYCalculator.urls')),  # http://127.0.0.1:8000
]

handler404 = page_not_found
