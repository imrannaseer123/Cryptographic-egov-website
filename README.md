# E-Governance Cryptography Web Application

A secure Django-based web application demonstrating end-to-end encrypted authentication, role-based dashboards, and two-factor authentication (2FA) with OTP verification.

## 🚀 Features

### 🔐 Security Features
- **Encrypted Credential Storage**: All usernames and passwords are encrypted using Fernet symmetric encryption
- **Two-Factor Authentication**: 6-digit OTP verification after successful login
- **Session Management**: Secure session handling with 30-minute timeout
- **CSRF Protection**: Built-in Django CSRF protection on all forms
- **Role-Based Access Control**: Different dashboards for Officer, Citizen1, and Citizen2 users

### 🎨 User Interface
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Modern UI**: Clean, professional design with gradient backgrounds and card layouts
- **Accessibility**: WCAG-compliant with proper ARIA labels and keyboard navigation
- **Interactive Elements**: Loading states, animations, and user feedback

### 👥 User Roles
1. **Officer**: Administrative dashboard with enhanced features
2. **Citizen1**: Basic citizen dashboard with personal information
3. **Citizen2**: Alternative citizen dashboard with different data

## 📋 Requirements

- Python 3.12+
- Django 4.2+
- Cryptography libraries
- SQLite database (included)

## 🛠️ Installation & Setup

### 1. Clone and Navigate
```bash
cd Crypto
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
The `.env` file is already configured with the necessary keys:
- Django SECRET_KEY
- Fernet ENCRYPTION_KEY for secure credential storage

### 4. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Seed test users with encrypted credentials
python manage.py seed_users
```

### 5. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

## 🔑 Test Credentials

After running the seed command, you can use these test credentials:

| Role | Username | Password |
|------|----------|----------|
| Officer | officer_test | Officer@123 |
| Citizen1 | citizen1_test | Citizen1@123 |
| Citizen2 | citizen2_test | Citizen2@123 |

## 🎯 How to Use

### Authentication Flow
1. Navigate to `http://127.0.0.1:8000/login/`
2. Enter username, password, and select your role
3. Check the console for the 6-digit OTP code
4. Enter the OTP on the verification page
5. Access your role-specific dashboard

### Dashboard Features
- **Officer Dashboard**: Administrative features, clearance levels, emergency contacts
- **Citizen Dashboards**: Personal information, service requests, registration details
- **Session Management**: Automatic logout after 30 minutes of inactivity
- **Security Indicators**: Visual feedback for encrypted data and secure connections

## 🏗️ Project Structure

```
Crypto/
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables
├── db.sqlite3                   # SQLite database
├── egovernance/                 # Django project directory
│   ├── __init__.py
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # Main URL routing
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
├── authentication/              # Authentication app
│   ├── __init__.py
│   ├── models.py                # UserProfile model with encryption
│   ├── views.py                 # Authentication and dashboard views
│   ├── forms.py                 # Login and OTP forms
│   ├── utils.py                 # Encryption/decryption utilities
│   ├── urls.py                  # App-specific URL routing
│   ├── admin.py                 # Django admin configuration
│   ├── management/              # Django management commands
│   │   └── commands/
│   │       └── seed_users.py    # User seeding command
│   └── migrations/              # Database migrations
├── templates/                   # HTML templates
│   ├── base.html                # Base template with Bootstrap
│   ├── login.html               # Login form page
│   ├── otp_verification.html    # OTP verification page
│   ├── officer_dashboard.html   # Officer dashboard
│   ├── citizen1_dashboard.html  # Citizen1 dashboard
│   └── citizen2_dashboard.html  # Citizen2 dashboard
├── static/                      # Static files
│   ├── css/
│   │   └── style.css            # Custom CSS styles
│   └── js/
│       └── main.js              # JavaScript functionality
└── staticfiles/                 # Collected static files
```

## 🔒 Security Implementation

### Encryption Details
- **Algorithm**: Fernet symmetric encryption (AES 128 in CBC mode)
- **Key Derivation**: PBKDF2 with SHA-256 and 480,000 iterations
- **Storage**: All credentials stored encrypted in database
- **Environment**: Encryption keys stored in `.env` file

### Authentication Flow
1. User enters credentials → Encrypted for comparison
2. Successful validation → Generate 6-digit OTP
3. OTP displayed in console (testing) → User enters OTP
4. OTP verification → Create authenticated session
5. Role-based dashboard access → Secure session management

### Security Headers
- Session cookies: HTTPOnly, Secure, SameSite
- CSRF tokens: Enabled on all forms
- Content Security Policy: Configured for production
- SSL Redirect: Enabled in production environment

## 🧪 Testing

### Management Commands
```bash
# Generate new encryption key
python manage.py seed_users --generate-key

# Reset and reseed users
python manage.py seed_users --reset

# Verbose output
python manage.py seed_users --verbose
```

### Manual Testing Steps
1. **Login Flow**: Test all three user roles
2. **OTP Verification**: Verify 6-digit code from console
3. **Dashboard Access**: Test role-based access control
4. **Session Management**: Test session timeout and logout
5. **Security**: Test direct URL access without authentication

### Database Verification
```bash
# Access Django shell
python manage.py shell

# Verify encrypted data
from authentication.models import UserProfile
users = UserProfile.objects.all()
for user in users:
    print(f"Role: {user.role}, Encrypted: {user.username_encrypted[:20]}...")
```

## 🔧 Development

### Adding New Features
1. Update models in `authentication/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Update views in `authentication/views.py`
4. Add/modify templates in `templates/`
5. Update URL routing in `authentication/urls.py`

### Customizing Encryption
- Modify encryption logic in `authentication/utils.py`
- Update ENCRYPTION_KEY in `.env` file
- Test with `python manage.py seed_users --reset`

### Styling Changes
- Edit `static/css/style.css` for custom styles
- Modify templates for layout changes
- Use Bootstrap 5 classes for responsive design

## 📱 Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the console output for error messages
2. Verify `.env` configuration
3. Ensure all dependencies are installed
4. Test with the provided management commands

---

**⚡ Built with Django, Bootstrap 5, and modern cryptography practices**

#to Run the project
< your path >/Crypto-compyle-test-crypto-egov> python manage.py runserver
    
