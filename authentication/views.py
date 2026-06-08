"""
Authentication views for the E-Governance portal.

This module provides views for secure login, OTP verification, and
role-based dashboard access with proper session management.
"""

import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.conf import settings
from .models import UserProfile
from .forms import LoginForm, OTPForm
from .utils import generate_otp, verify_otp_format

logger = logging.getLogger(__name__)


def login_required_custom(view_func):
    """
    Custom decorator to require authentication.

    Args:
        view_func: View function to protect

    Returns:
        Wrapped view function that checks authentication
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get('authenticated', False):
            messages.error(request, 'Please login to access this page.')
            return redirect(reverse('authentication:login'))

        if not request.session.get('user_id'):
            messages.error(request, 'Session expired. Please login again.')
            request.session.flush()
            return redirect(reverse('authentication:login'))

        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(required_role):
    """
    Decorator to require specific user role.

    Args:
        required_role (str): Required role to access the view

    Returns:
        Decorator function that checks user role
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.session.get('authenticated', False):
                messages.error(request, 'Please login to access this page.')
                return redirect(reverse('authentication:login'))

            user_role = request.session.get('user_role')
            if user_role != required_role:
                messages.error(request, 'Access denied. You do not have permission to access this page.')
                return redirect(reverse('authentication:login'))

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login with encrypted credential validation.

    GET: Display login form
    POST: Validate credentials and generate OTP
    """
    # Redirect if already authenticated
    if request.session.get('authenticated', False):
        dashboard_url = request.session.get('dashboard_url', 'authentication:login')
        if ':' not in dashboard_url:
            dashboard_url = 'authentication:login'
        return redirect(reverse(dashboard_url))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            remember_me = form.cleaned_data.get('remember_me', False)

            try:
                # Find user by encrypted credentials
                user = UserProfile.find_by_credentials(username, password, role)

                if user and user.is_active:
                    # Generate OTP
                    otp_code = generate_otp()

                    # Store OTP in session with timestamp
                    request.session['otp'] = {
                        'code': otp_code,
                        'timestamp': timezone.now().isoformat(),
                        'attempts': 0,
                        'user_id': user.id,
                        'username': username,
                        'role': role
                    }

                    # Set session expiry based on remember me
                    if remember_me:
                        request.session.set_expiry(7 * 24 * 60 * 60)  # 7 days
                    else:
                        request.session.set_expiry(30 * 60)  # 30 minutes

                    # Log OTP for testing (in production, this would be sent via SMS/email)
                    print(f"\n{'='*50}")
                    print(f"OTP CODE FOR TESTING: {otp_code}")
                    print(f"User: {username} ({role})")
                    print(f"{'='*50}\n")

                    logger.info(f"OTP generated for user {username} with role {role}")

                    messages.success(request, 'Login successful! Please enter the OTP code displayed in your console.')
                    return redirect('authentication:otp_verification')
                else:
                    messages.error(request, 'Invalid credentials or account inactive. Please try again.')
                    logger.warning(f"Failed login attempt for username: {username}, role: {role}")

            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                messages.error(request, 'An error occurred during login. Please try again.')
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'title': 'Login - E-Governance Portal'
    })


@csrf_protect
@require_http_methods(["GET", "POST"])
def otp_view(request):
    """
    Handle OTP verification for two-factor authentication.

    GET: Display OTP verification form
    POST: Verify OTP and complete authentication
    """
    # Check if OTP exists in session
    otp_data = request.session.get('otp')
    if not otp_data:
        messages.error(request, 'Session expired or invalid. Please login again.')
        return redirect('authentication:login')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp_code']

            try:
                # Check OTP expiry (5 minutes)
                otp_timestamp = datetime.fromisoformat(otp_data['timestamp'])
                if timezone.now() - otp_timestamp > timedelta(minutes=5):
                    messages.error(request, 'OTP has expired. Please login again.')
                    del request.session['otp']
                    return redirect('authentication:login')

                # Check maximum attempts (3)
                if otp_data['attempts'] >= 3:
                    messages.error(request, 'Maximum OTP attempts reached. Please login again.')
                    del request.session['otp']
                    return redirect('authentication:login')

                # Verify OTP
                if entered_otp == otp_data['code']:
                    # OTP verification successful
                    user_id = otp_data['user_id']
                    user = UserProfile.objects.get(id=user_id)

                    # Create authenticated session
                    request.session['authenticated'] = True
                    request.session['user_id'] = user.id
                    request.session['username'] = otp_data['username']
                    request.session['user_role'] = otp_data['role']
                    request.session['dashboard_url'] = user.get_dashboard_url()
                    request.session['login_time'] = timezone.now().isoformat()

                    # Clear OTP data
                    del request.session['otp']

                    logger.info(f"User {user.get_username()} ({user.role}) authenticated successfully")

                    messages.success(request, f'Welcome, {user.get_username()}! Redirecting to your dashboard...')
                    return redirect(user.get_dashboard_url())
                else:
                    # Invalid OTP
                    otp_data['attempts'] += 1
                    request.session['otp'] = otp_data
                    remaining_attempts = 3 - otp_data['attempts']

                    if remaining_attempts > 0:
                        messages.error(request, f'Invalid OTP. {remaining_attempts} attempt(s) remaining.')
                    else:
                        messages.error(request, 'Maximum OTP attempts reached. Please login again.')
                        del request.session['otp']
                        return redirect('authentication:login')

                    logger.warning(f"Invalid OTP attempt for user ID: {user_id}")

            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found. Please login again.')
                del request.session['otp']
                return redirect('authentication:login')

            except Exception as e:
                logger.error(f"OTP verification error: {str(e)}")
                messages.error(request, 'An error occurred during OTP verification. Please try again.')
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = OTPForm()

    return render(request, 'otp_verification.html', {
        'form': form,
        'title': 'OTP Verification - E-Governance Portal',
        'otp_info': {
            'expires_in': 5,  # minutes
            'max_attempts': 3,
            'current_attempts': otp_data.get('attempts', 0) if otp_data else 0
        }
    })


@login_required_custom
@role_required('officer')
def officer_dashboard(request):
    """
    Officer dashboard with profile information.

    Requires officer role and authenticated session.
    """
    try:
        user_id = request.session.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        dashboard_data = user.get_dashboard_data()

        return render(request, 'officer_dashboard.html', {
            'user': user,
            'dashboard_data': dashboard_data,
            'title': f"Officer Dashboard - {user.get_username()}",
            'session_info': {
                'login_time': request.session.get('login_time'),
                'role': request.session.get('user_role'),
                'username': request.session.get('username')
            }
        })
    except UserProfile.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect(reverse('authentication:login'))
    except Exception as e:
        logger.error(f"Officer dashboard error: {str(e)}")
        messages.error(request, 'An error occurred loading your dashboard.')
        return redirect(reverse('authentication:login'))


@login_required_custom
@role_required('citizen1')
def citizen1_dashboard(request):
    """
    Citizen1 dashboard with profile information.

    Requires citizen1 role and authenticated session.
    """
    try:
        user_id = request.session.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        dashboard_data = user.get_dashboard_data()

        return render(request, 'citizen1_dashboard.html', {
            'user': user,
            'dashboard_data': dashboard_data,
            'title': f"Citizen Dashboard - {user.get_username()}",
            'session_info': {
                'login_time': request.session.get('login_time'),
                'role': request.session.get('user_role'),
                'username': request.session.get('username')
            }
        })
    except UserProfile.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect(reverse('authentication:login'))
    except Exception as e:
        logger.error(f"Citizen1 dashboard error: {str(e)}")
        messages.error(request, 'An error occurred loading your dashboard.')
        return redirect(reverse('authentication:login'))


@login_required_custom
@role_required('citizen2')
def citizen2_dashboard(request):
    """
    Citizen2 dashboard with profile information.

    Requires citizen2 role and authenticated session.
    """
    try:
        user_id = request.session.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        dashboard_data = user.get_dashboard_data()

        return render(request, 'citizen2_dashboard.html', {
            'user': user,
            'dashboard_data': dashboard_data,
            'title': f"Citizen Dashboard - {user.get_username()}",
            'session_info': {
                'login_time': request.session.get('login_time'),
                'role': request.session.get('user_role'),
                'username': request.session.get('username')
            }
        })
    except UserProfile.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect(reverse('authentication:login'))
    except Exception as e:
        logger.error(f"Citizen2 dashboard error: {str(e)}")
        messages.error(request, 'An error occurred loading your dashboard.')
        return redirect(reverse('authentication:login'))


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Handle user logout and session cleanup.

    GET: Show logout confirmation
    POST: Process logout and clear session
    """
    if request.method == 'POST':
        username = request.session.get('username', 'Unknown')
        role = request.session.get('user_role', 'Unknown')

        # Clear session data
        request.session.flush()

        logger.info(f"User {username} ({role}) logged out successfully")
        messages.success(request, 'You have been logged out successfully.')
        return redirect('authentication:login')

    # GET request - show confirmation
    return render(request, 'logout_confirmation.html', {
        'title': 'Logout - E-Governance Portal',
        'username': request.session.get('username', 'User')
    })


def access_denied(request):
    """
    Access denied page for unauthorized access attempts.
    """
    return render(request, 'access_denied.html', {
        'title': 'Access Denied - E-Governance Portal'
    })


def home_view(request):
    """
    Redirect to login page or appropriate dashboard based on authentication status.
    """
    if request.session.get('authenticated', False):
        dashboard_url = request.session.get('dashboard_url', 'authentication:login')
        if ':' not in dashboard_url:
            dashboard_url = 'authentication:login'
        return redirect(reverse(dashboard_url))
    else:
        return redirect('authentication:login')
