from django.contrib import admin
from django.urls import path
from scanner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/record_scan/', views.record_scan, name='record_scan'),
    path('api/logs/', views.get_logs, name='get_logs'),
    path('', views.user_portal_view, name='dashboard'),
    path('api/link_card/', views.link_card, name='link_card'),
    path('api/check_scanner/', views.check_scanner_status, name='check_scanner'),
    path('admin_portal.html', views.dashboard, name='admin_portal'),
    path('edit_user.html', views.edit_user_view, name='edit_user'),
    path('user-portal/', views.user_portal_view, name='user_portal'),
    path('save_user.html', views.save_user_view, name='save_user'),
    path('api/get_user/', views.get_user_details, name='get_user'),
    path('api/update_user/', views.update_user, name='update_user'),
    path('api/save_supply/', views.save_supply, name='save_supply'),
    path('api/get_admin_logs/', views.get_admin_logs, name='get_admin_logs'),
    path('api/assign_supply/', views.assign_supply, name='assign_supply'),
    path('api/get_recipients/', views.get_recipients, name='get_recipients'),
    path('recipients.html', views.recipients_view, name='recipients'),
    path('index.html', views.index_view, name='index'),
    path('api/manual_login/', views.manual_login, name='manual_login'),
    path('api/get_user_records/', views.get_user_records, name='get_user_records'),
    path('api/ping/', views.api_ping, name='api_ping'),
]

