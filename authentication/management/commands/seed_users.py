"""
Django management command to seed test users with encrypted credentials.

This command creates test users for the E-Governance portal with
encrypted usernames and passwords for secure authentication testing.
"""

import os
from django.core.management.base import BaseCommand
from django.db import transaction
from decouple import config
from authentication.models import UserProfile
from authentication.utils import encrypt_data, generate_test_encryption_key, validate_encryption_key


class Command(BaseCommand):
    help = 'Seed test users with encrypted credentials for the E-Governance portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing users before seeding new ones',
        )
        parser.add_argument(
            '--generate-key',
            action='store_true',
            help='Generate and display a new encryption key',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output during seeding process',
        )

    def handle(self, *args, **options):
        self.verbose = options.get('verbose', False)

        self.stdout.write(self.style.SUCCESS('🚀 Starting E-Governance user seeding process...'))

        # Generate encryption key if requested
        if options.get('generate_key'):
            self.generate_encryption_key()

        # Check encryption key
        self.check_encryption_key()

        # Reset existing users if requested
        if options.get('reset'):
            self.reset_existing_users()

        # Seed test users
        self.seed_test_users()

        self.stdout.write(self.style.SUCCESS('✅ User seeding completed successfully!'))

    def generate_encryption_key(self):
        """Generate and display a new Fernet encryption key."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('🔑 Generating new encryption key...'))

        key = generate_test_encryption_key()

        self.stdout.write(self.style.SUCCESS(f'Generated ENCRYPTION_KEY: {key}'))
        self.stdout.write('\nAdd this to your .env file:')
        self.stdout.write(self.style.HTTP_INFO('ENCRYPTION_KEY=' + key))
        self.stdout.write('='*60 + '\n')

    def check_encryption_key(self):
        """Verify that encryption key is properly configured."""
        try:
            encryption_key = config('ENCRYPTION_KEY', default='')
            if not encryption_key:
                self.stdout.write(
                    self.style.ERROR('❌ ENCRYPTION_KEY not found in environment variables!')
                )
                self.stdout.write(
                    self.style.WARNING('💡 Run with --generate-key to create a new key')
                )
                raise ValueError('ENCRYPTION_KEY not configured')

            if not validate_encryption_key(encryption_key):
                self.stdout.write(
                    self.style.ERROR('❌ Invalid ENCRYPTION_KEY format!')
                )
                raise ValueError('Invalid ENCRYPTION_KEY format')

            if self.verbose:
                self.stdout.write(
                    self.style.SUCCESS('✅ Encryption key validated successfully')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Encryption key validation failed: {str(e)}')
            )
            raise

    def reset_existing_users(self):
        """Delete existing test users."""
        try:
            count = UserProfile.objects.count()
            if count > 0:
                self.stdout.write(
                    self.style.WARNING(f'🗑️  Deleting {count} existing users...')
                )
                UserProfile.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('✅ Existing users deleted successfully')
                )
            else:
                self.stdout.write(
                    self.style.INFO('ℹ️  No existing users to delete')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to reset existing users: {str(e)}')
            )
            raise

    @transaction.atomic
    def seed_test_users(self):
        """Create test users with encrypted credentials."""
        test_users = [
            {
                'username': 'officer_test',
                'password': 'Officer@123',
                'role': 'officer',
                'description': 'Officer with administrative access'
            },
            {
                'username': 'citizen1_test',
                'password': 'Citizen1@123',
                'role': 'citizen1',
                'description': 'Citizen 1 with basic access'
            },
            {
                'username': 'citizen2_test',
                'password': 'Citizen2@123',
                'role': 'citizen2',
                'description': 'Citizen 2 with basic access'
            },
        ]

        created_users = []

        self.stdout.write('\n👥 Creating test users...')

        for user_data in test_users:
            try:
                # Check if user already exists
                existing_users = UserProfile.objects.filter(role=user_data['role'])
                if existing_users.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  User with role '{user_data['role']}' already exists. Skipping..."
                        )
                    )
                    continue

                # Create new user with encrypted credentials
                user = UserProfile()
                user.set_username(user_data['username'])
                user.set_password(user_data['password'])
                user.role = user_data['role']
                user.is_active = True
                user.save()

                created_users.append(user)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Created {user_data['role']}: {user_data['username']}"
                    )
                )

                if self.verbose:
                    self.stdout.write(
                        self.style.HTTP_INFO(
                            f"   └─ Description: {user_data['description']}"
                        )
                    )
                    self.stdout.write(
                        self.style.HTTP_INFO(
                            f"   └─ User ID: {user.id}"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Failed to create user {user_data['username']}: {str(e)}"
                    )
                )
                raise

        # Display summary
        if created_users:
            self.stdout.write('\n' + '='*60)
            self.stdout.write(
                self.style.SUCCESS(f'🎉 Successfully created {len(created_users)} test users!')
            )

            self.stdout.write('\n📋 Test Credentials:')
            self.stdout.write(self.style.HTTP_INFO('─' * 40))

            for user_data in test_users:
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f"🔐 {user_data['role'].title()}: {user_data['username']} / {user_data['password']}"
                    )
                )

            self.stdout.write('\n💡 Usage Instructions:')
            self.stdout.write('1. Start the development server: python manage.py runserver')
            self.stdout.write('2. Navigate to: http://127.0.0.1:8000/login/')
            self.stdout.write('3. Use the credentials above to test different user roles')
            self.stdout.write('4. Check console for OTP codes during login')

            self.stdout.write('\n🔒 Security Information:')
            self.stdout.write('• All passwords are encrypted using Fernet symmetric encryption')
            self.stdout.write('• Two-factor authentication (OTP) is required for login')
            self.stdout.write('• OTP codes are displayed in the console for testing')
            self.stdout.write('• Session timeout is set to 30 minutes')

            self.stdout.write('='*60)
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  No new users were created (they may already exist)')
            )

    def display_system_info(self):
        """Display system information and configuration."""
        self.stdout.write('\n📊 System Information:')
        self.stdout.write('─' * 30)

        # Database info
        try:
            total_users = UserProfile.objects.count()
            active_users = UserProfile.objects.filter(is_active=True).count()

            self.stdout.write(f'📊 Total Users: {total_users}')
            self.stdout.write(f'✅ Active Users: {active_users}')

            # Users by role
            roles = ['officer', 'citizen1', 'citizen2']
            for role in roles:
                count = UserProfile.objects.filter(role=role, is_active=True).count()
                self.stdout.write(f'👤 {role.title()}s: {count}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to retrieve system info: {str(e)}')
            )

        # Environment info
        self.stdout.write('\n🌍 Environment:')
        self.stdout.write(f'🔧 Debug Mode: {config("DEBUG", default=False)}')
        self.stdout.write(f'🌐 Allowed Hosts: {config("ALLOWED_HOSTS", default="localhost,127.0.0.1")}')
        self.stdout.write(f'🔐 Encryption Key: {"✅ Configured" if config("ENCRYPTION_KEY") else "❌ Not Configured"}')