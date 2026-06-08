"""
Database models for the authentication app.

This module defines the UserProfile model with encrypted credential storage
for secure authentication and role-based access control.
"""

from django.db import models
from django.core.exceptions import ValidationError
from .utils import encrypt_data, decrypt_data


class UserProfile(models.Model):
    """
    User profile model with encrypted credentials and role-based access.

    Stores user credentials in encrypted form for security, along with role
    information for access control to different dashboard views.
    """

    ROLE_CHOICES = [
        ('officer', 'Officer'),
        ('citizen1', 'Citizen1'),
        ('citizen2', 'Citizen2'),
    ]

    username_encrypted = models.CharField(max_length=256)
    password_encrypted = models.CharField(max_length=256)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="User role determines dashboard access"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this user account is active"
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        """Return encrypted identifier for admin display."""
        return f"UserProfile #{self.id} ({self.role})"

    # Username encryption/decryption methods
    def set_username(self, username: str):
        """
        Encrypt and store username.

        Args:
            username (str): Plain text username to encrypt and store
        """
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        self.username_encrypted = encrypt_data(username.strip())

    def get_username(self) -> str:
        """
        Decrypt and return username.

        Returns:
            str: Decrypted username
        """
        try:
            return decrypt_data(self.username_encrypted)
        except Exception as e:
            raise ValueError(f"Failed to decrypt username: {str(e)}")

    # Password encryption/decryption methods
    def set_password(self, password: str):
        """
        Encrypt and store password.

        Args:
            password (str): Plain text password to encrypt and store
        """
        if not password or not password.strip():
            raise ValidationError("Password cannot be empty")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        self.password_encrypted = encrypt_data(password)

    def get_password(self) -> str:
        """
        Decrypt and return password.

        Returns:
            str: Decrypted password
        """
        try:
            return decrypt_data(self.password_encrypted)
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {str(e)}")

    # Authentication methods
    def verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify provided username and password against stored encrypted values.

        Args:
            username (str): Username to verify
            password (str): Password to verify

        Returns:
            bool: True if credentials match, False otherwise
        """
        try:
            stored_username = self.get_username()
            stored_password = self.get_password()
            return (username == stored_username and
                   password == stored_password and
                   self.is_active)
        except Exception:
            return False

    @classmethod
    def find_by_credentials(cls, username: str, password: str, role: str):
        """
        Find user profile by credentials.

        Args:
            username (str): Username to search for
            password (str): Password to verify
            role (str): User role to match

        Returns:
            UserProfile: Matching user profile or None
        """
        try:
            profiles = cls.objects.filter(role=role, is_active=True)
            for profile in profiles:
                if profile.verify_credentials(username, password):
                    return profile
        except Exception:
            pass
        return None

    # Role-based access methods
    def has_role(self, role: str) -> bool:
        """
        Check if user has specified role.

        Args:
            role (str): Role to check

        Returns:
            bool: True if user has the role, False otherwise
        """
        return self.role == role and self.is_active

    def can_access_dashboard(self, dashboard_role: str) -> bool:
        """
        Check if user can access specific dashboard.

        Args:
            dashboard_role (str): Role of the dashboard to access

        Returns:
            bool: True if user can access the dashboard, False otherwise
        """
        return self.role == dashboard_role and self.is_active

    # Convenience methods for role checks
    def is_officer(self) -> bool:
        """Check if user is an officer."""
        return self.has_role('officer')

    def is_citizen1(self) -> bool:
        """Check if user is citizen1."""
        return self.has_role('citizen1')

    def is_citizen2(self) -> bool:
        """Check if user is citizen2."""
        return self.has_role('citizen2')

    def get_dashboard_url(self) -> str:
        """
        Get the dashboard URL for this user's role.

        Returns:
            str: Dashboard URL name with namespace
        """
        dashboard_urls = {
            'officer': 'authentication:officer_dashboard',
            'citizen1': 'authentication:citizen1_dashboard',
            'citizen2': 'authentication:citizen2_dashboard',
        }
        return dashboard_urls.get(self.role, 'authentication:login')

    def get_role_display_name(self) -> str:
        """
        Get human-readable role name.

        Returns:
            str: Human-readable role name
        """
        role_names = {
            'officer': 'Officer',
            'citizen1': 'Citizen 1',
            'citizen2': 'Citizen 2',
        }
        return role_names.get(self.role, 'Unknown')

    # Dashboard data methods
    def get_dashboard_data(self) -> dict:
        """
        Get fictional dashboard data based on user role.

        Returns:
            dict: Role-specific dashboard data
        """
        if self.role == 'officer':
            return {
                "type": "fictional_officer",
                "name": "Akash R. Patel",
                "temporary_id": "TMP-OFF-2025-0149",
                "rank": "Inspecting Officer (Temporary Assignment)",
                "unit": "Field Operations — Zone 7",
                "issued_by": "Central Command (Test)",
                "contact_phone_masked": "+91-98XXXXXX45",
                "email_masked": "akash.patel@example.test",
                "address_temp": "Block 12, Transit Housing, Sector 9, Test City",
                "date_of_assignment": "2025-10-01",
                "assignment_expiry": "2025-10-31",
                "clearance_level_temp": "LEVEL-T3",
                "temporary_badge_code": "B-7-4491",
                "emergency_contact": {
                    "name": "Rita Patel (fictional)",
                    "relation": "spouse",
                    "phone_masked": "+91-98XXXXXX22"
                },
                "notes": "Test profile only — do not use for decision-making."
            }
        elif self.role == 'citizen1':
            return {
                "type": "fictional_citizen",
                "name": "Nazeer K. Shaikh",
                "temporary_citizen_id": "TMP-CIT-2025-337",
                "nationality": "Fictionland",
                "contact_phone_masked": "+91-97XXXXXX88",
                "email_masked": "nazeer.shaikh@example.test",
                "temp_address": "Room 204, Visitor Housing, Test City",
                "date_of_registration": "2025-10-15",
                "purpose_of_visit": "Temporary documentation update (fictional)",
                "identification_presented": "Fictionland Driver ID (masked)",
                "notes": "Fictional test data only."
            }
        elif self.role == 'citizen2':
            return {
                "type": "fictional_citizen",
                "name": "Priya S. Kumar",
                "temporary_citizen_id": "TMP-CIT-2025-338",
                "nationality": "Fictionland",
                "contact_phone_masked": "+91-93XXXXXX76",
                "email_masked": "priya.kumar@example.test",
                "temp_address": "Room 205, Visitor Housing, Test City",
                "date_of_registration": "2025-10-16",
                "purpose_of_visit": "Temporary service request (fictional)",
                "identification_presented": "Fictionland Passport ID (masked)",
                "notes": "Fictional test data only."
            }
        else:
            return {
                "type": "unknown",
                "name": "Unknown User",
                "notes": "No data available for this role."
            }