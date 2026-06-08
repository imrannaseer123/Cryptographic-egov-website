#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'egovernance.settings')
django.setup()

from authentication.models import UserProfile

def test_dashboard_url():
    # Test finding user by credentials
    user = UserProfile.find_by_credentials('officer_test', 'Officer@123', 'officer')
    print('User found:', user)
    if user:
        print('Dashboard URL:', user.get_dashboard_url())
        print('User ID:', user.id)
        print('Role:', user.role)
        print('Is active:', user.is_active)
    else:
        print('No user found with those credentials')

if __name__ == '__main__':
    test_dashboard_url()
