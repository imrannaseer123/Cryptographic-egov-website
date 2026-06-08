"""
URL configuration for the authentication app.

Defines URL patterns for login, OTP verification, dashboard access,
and other authentication-related functionality.
"""

from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('otp/', views.otp_view, name='otp_verification'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard URLs (role-based)
    path('officer_dashboard/', views.officer_dashboard, name='officer_dashboard'),
    path('citizen1_dashboard/', views.citizen1_dashboard, name='citizen1_dashboard'),
    path('citizen2_dashboard/', views.citizen2_dashboard, name='citizen2_dashboard'),

    # Utility URLs
    path('access-denied/', views.access_denied, name='access_denied'),
    path('', views.home_view, name='home'),
]