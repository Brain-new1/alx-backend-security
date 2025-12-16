from django.contrib import admin
from django.urls import path
from ip_tracking.views import (
    home, login_view, logout_view, dashboard,
    logs_view, blocked_ips, block_ip, unblock_ip, unblock_history
)

urlpatterns = [
    # Public routes
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),

    # Logs
    path('logs/', logs_view, name='logs'),

    # Blocked IP Management
    path('blocked/', blocked_ips, name='blocked_ips'),
    path('block/', block_ip, name='block_ip'),
    path('unblock/<str:ip>/', unblock_ip, name='unblock_ip'),
    path("unblock-history/", unblock_history, name="unblock_history"),
]
