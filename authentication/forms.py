"""
Django forms for authentication and OTP verification.

This module defines forms for user login with role selection and
OTP verification with Bootstrap 5 styling using crispy forms.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from crispy_bootstrap5.bootstrap5 import BS5Accordion
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .utils import verify_otp_format


class LoginForm(forms.Form):
    """
    Login form with username, password, and role selection.

    Includes Bootstrap 5 styling and client-side validation.
    """

    username = forms.CharField(
        label=_("Username"),
        max_length=50,
        min_length=3,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
                'autofocus': True,
                'pattern': '[a-zA-Z0-9_]{3,50}',
                'title': 'Username must be 3-50 characters, alphanumeric only'
            }
        ),
        help_text=_("Username must be 3-50 characters, alphanumeric only")
    )

    password = forms.CharField(
        label=_("Password"),
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
                'minlength': '8',
                'title': 'Password must be at least 8 characters long'
            }
        ),
        help_text=_("Password must be at least 8 characters long")
    )

    role = forms.ChoiceField(
        label=_("Role"),
        choices=[
            ('', _('-- Select Your Role --')),
            ('officer', _('Officer')),
            ('citizen1', _('Citizen 1')),
            ('citizen2', _('Citizen 2')),
        ],
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'title': 'Select your role to access the appropriate dashboard'
            }
        ),
        help_text=_("Select your role to access the appropriate dashboard")
    )

    remember_me = forms.BooleanField(
        label=_("Remember me"),
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'login'
        self.helper.attrs = {
            'novalidate': 'true',  # Enable custom validation
            'data-parsley-validate': ''
        }

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("""
                    <div class="text-center mb-4">
                        <h4 class="text-primary">E-Governance Portal</h4>
                        <p class="text-muted">Secure Authentication System</p>
                    </div>
                    """),
                    css_class='col-12'
                ),
                css_class='row'
            ),
            Field(
                'username',
                css_class='mb-3',
                wrapper_class='form-group',
                label_class='form-label fw-semibold'
            ),
            Field(
                'password',
                css_class='mb-3',
                wrapper_class='form-group',
                label_class='form-label fw-semibold'
            ),
            Field(
                'role',
                css_class='mb-3',
                wrapper_class='form-group',
                label_class='form-label fw-semibold'
            ),
            Div(
                Field(
                    'remember_me',
                    css_class='form-check-input me-2',
                    wrapper_class='form-check mb-3'
                ),
                css_class='mb-3'
            ),
            Div(
                Submit(
                    'submit',
                    _('Login & Continue'),
                    css_class='btn btn-primary btn-lg w-100',
                    css_id='login-submit-btn'
                ),
                css_class='mb-3'
            ),
            HTML("""
            <div class="text-center">
                <small class="text-muted">
                    <i class="fas fa-lock me-1"></i>
                    Your credentials are encrypted and secure
                </small>
            </div>
            """)
        )

    def clean_username(self):
        """Validate username format."""
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError(_("Username is required."))

        username = username.strip()
        if not username.isalnum() and '_' not in username:
            raise ValidationError(_("Username can only contain letters, numbers, and underscores."))

        return username

    def clean_password(self):
        """Validate password complexity."""
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError(_("Password is required."))

        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))

        # You can add more complex validation here if needed
        return password

    def clean_role(self):
        """Validate role selection."""
        role = self.cleaned_data.get('role')
        if not role:
            raise ValidationError(_("Please select your role."))

        valid_roles = ['officer', 'citizen1', 'citizen2']
        if role not in valid_roles:
            raise ValidationError(_("Invalid role selected."))

        return role


class OTPForm(forms.Form):
    """
    OTP verification form for two-factor authentication.

    Includes numeric validation and auto-focus features.
    """

    otp_code = forms.CharField(
        label=_("One-Time Password"),
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg text-center',
                'placeholder': '000000',
                'autofocus': True,
                'pattern': '[0-9]{6}',
                'title': 'Enter 6-digit OTP code',
                'maxlength': '6',
                'inputmode': 'numeric',
                'autocomplete': 'one-time-code'
            }
        ),
        help_text=_("Enter the 6-digit OTP code displayed in your console")
    )

    resend_otp = forms.BooleanField(
        label=_("Resend OTP"),
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'otp_verification'
        self.helper.attrs = {
            'novalidate': 'true',
            'data-parsley-validate': ''
        }

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("""
                    <div class="text-center mb-4">
                        <h4 class="text-primary">Verify Your Identity</h4>
                        <p class="text-muted">Enter the 6-digit OTP code</p>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            OTP code is displayed in the console for testing
                        </div>
                    </div>
                    """),
                    css_class='col-12'
                ),
                css_class='row'
            ),
            Field(
                'otp_code',
                css_class='mb-4',
                wrapper_class='form-group',
                label_class='form-label fw-semibold text-center'
            ),
            Div(
                Submit(
                    'submit',
                    _('Verify OTP'),
                    css_class='btn btn-success btn-lg w-100',
                    css_id='otp-submit-btn'
                ),
                css_class='mb-3'
            ),
            HTML("""
            <div class="d-flex justify-content-between align-items-center">
                <a href="{% url 'login' %}" class="btn btn-outline-secondary btn-sm">
                    <i class="fas fa-arrow-left me-1"></i> Back to Login
                </a>
                <small class="text-muted">
                    OTP expires in 5 minutes
                </small>
            </div>
            """)
        )

    def clean_otp_code(self):
        """Validate OTP format."""
        otp_code = self.cleaned_data.get('otp_code')
        if not otp_code:
            raise ValidationError(_("OTP code is required."))

        if not verify_otp_format(otp_code):
            raise ValidationError(_("OTP must be exactly 6 digits."))

        return otp_code

    def clean(self):
        """Custom validation for OTP verification."""
        cleaned_data = super().clean()
        otp_code = cleaned_data.get('otp_code')

        if otp_code and not verify_otp_format(otp_code):
            raise ValidationError(_("Invalid OTP format. Please enter exactly 6 digits."))

        return cleaned_data


class ResendOTPForm(forms.Form):
    """
    Simple form for requesting OTP resend.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'd-inline'