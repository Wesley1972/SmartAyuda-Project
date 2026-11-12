from django.contrib import admin
from django.urls import path
from scanner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/record_scan/', views.record_scan, name='record_scan'),
    path('api/logs/', views.get_logs, name='get_logs'),  # New API route for JavaScript
    path('', views.dashboard, name='dashboard'),         # New route for the homepage
]
