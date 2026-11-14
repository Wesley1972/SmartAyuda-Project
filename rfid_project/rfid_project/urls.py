from django.contrib import admin
from django.urls import path
from scanner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/record_scan/', views.record_scan, name='record_scan'),
    path('api/logs/', views.get_logs, name='get_logs'),  # New API route for JavaScript
    path('', views.dashboard, name='dashboard'),         # New route for the homepage
    path('api/link_card/', views.link_card, name='link_card'), # New endpoint for linking a card to a user
    path('api/check_scanner/', views.check_scanner_status, name='check_scanner'),
    path('admin_portal.html', views.dashboard, name='admin_portal'),
    path('edit_user.html', views.edit_user_view, name='edit_user'),
]





