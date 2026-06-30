from django.core.management.base import BaseCommand

from accounts.models import User

DEFAULT_PASSWORD = 'password.123'

SEED_USERS = [
    {
        'username': 'admin',
        'role': 'admin',
        'first_name': 'System',
        'last_name': 'Administrator',
        'email': 'admin@tibaflow.local',
        'employee_id': 'EMP-ADMIN',
        'department': 'Administration',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'reception',
        'role': 'reception',
        'first_name': 'Rita',
        'last_name': 'Mwangi',
        'email': 'reception@tibaflow.local',
        'employee_id': 'EMP-REC',
        'department': 'Reception',
    },
    {
        'username': 'triage',
        'role': 'triage',
        'first_name': 'Tom',
        'last_name': 'Otieno',
        'email': 'triage@tibaflow.local',
        'employee_id': 'EMP-TRI',
        'department': 'Triage',
    },
    {
        'username': 'doctor',
        'role': 'doctor',
        'first_name': 'Dr. Anne',
        'last_name': 'Wanjiku',
        'email': 'doctor@tibaflow.local',
        'employee_id': 'EMP-DOC',
        'department': 'General Medicine',
    },
    {
        'username': 'pharmacy',
        'role': 'pharmacy',
        'first_name': 'Peter',
        'last_name': 'Kamau',
        'email': 'pharmacy@tibaflow.local',
        'employee_id': 'EMP-PHA',
        'department': 'Pharmacy',
    },
    {
        'username': 'lab',
        'role': 'lab',
        'first_name': 'Lucy',
        'last_name': 'Achieng',
        'email': 'lab@tibaflow.local',
        'employee_id': 'EMP-LAB',
        'department': 'Laboratory',
    },
    {
        'username': 'nurse',
        'role': 'nurse',
        'first_name': 'Grace',
        'last_name': 'Njeri',
        'email': 'nurse@tibaflow.local',
        'employee_id': 'EMP-NUR',
        'department': 'Nursing',
    },
]


class Command(BaseCommand):
    help = 'Create default staff users for each hospital role (password: password.123)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-passwords',
            action='store_true',
            help='Reset passwords to the default for existing seeded users',
        )

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for entry in SEED_USERS:
            username = entry['username']
            defaults = {
                'first_name': entry['first_name'],
                'last_name': entry['last_name'],
                'email': entry['email'],
                'role': entry['role'],
                'employee_id': entry['employee_id'],
                'department': entry['department'],
                'is_staff': entry.get('is_staff', False),
                'is_superuser': entry.get('is_superuser', False),
                'is_active': True,
            }

            user, created = User.objects.get_or_create(username=username, defaults=defaults)

            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created {username} ({entry["role"]})'))
            else:
                changed = False
                for field, value in defaults.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        changed = True
                if changed:
                    user.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'Updated {username} ({entry["role"]})'))
                else:
                    self.stdout.write(f'Exists: {username} ({entry["role"]})')

                if options['reset_passwords']:
                    user.set_password(DEFAULT_PASSWORD)
                    user.save()
                    self.stdout.write(self.style.WARNING(f'  Password reset for {username}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed complete.'))
        self.stdout.write(f'  Created: {created_count}  Updated: {updated_count}')
        self.stdout.write(f'  Default password for all seeded users: {DEFAULT_PASSWORD}')
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        for entry in SEED_USERS:
            self.stdout.write(f'  {entry["username"]:<12} {entry["role"]:<12} {DEFAULT_PASSWORD}')
