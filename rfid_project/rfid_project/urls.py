from django.contrib import admin
from django.urls import path
from scanner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/record_scan/', views.record_scan, name='record_scan'),
]