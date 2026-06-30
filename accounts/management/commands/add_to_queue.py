from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientVisit
from triage.models import TriageRecord
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Add patients to the doctor queue with triage data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of patients to add to queue (default: 5)',
        )
        parser.add_argument(
            '--doctor',
            type=str,
            default='doctor',
            help='Doctor username (default: doctor)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing queue before adding new patients',
        )

    def handle(self, *args, **options):
        count = options['count']
        doctor_username = options['doctor']
        clear = options['clear']

        # Get the doctor
        try:
            doctor = User.objects.get(username=doctor_username, role='doctor')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Doctor "{doctor_username}" not found. Run seed_users first.'))
            return

        # Get triage nurse
        try:
            triage_nurse = User.objects.get(username='triage')
        except User.DoesNotExist:
            triage_nurse = None

        if clear:
            # Clear existing waiting patients
            PatientVisit.objects.filter(status='with_doctor').delete()
            self.stdout.write(self.style.WARNING('Cleared existing queue.'))

        self.stdout.write(f'Adding {count} patients to queue for Dr. {doctor.get_full_name()}...')

        # Common symptoms
        symptoms = [
            'Fever and headache',
            'Chest pain and shortness of breath',
            'Stomach pain and nausea',
            'Joint pain and swelling',
            'Sore throat and cough',
            'Dizziness and fatigue',
            'Back pain and muscle stiffness',
            'Skin rash and itching',
            'Ear pain and discharge',
            'Urinary pain and frequency',
            'Severe headache and blurred vision',
            'Persistent cough and fever',
            'Abdominal pain and vomiting',
            'Chest pain radiating to arm',
            'Difficulty breathing and wheezing'
        ]

        patients_added = 0

        for i in range(count):
            # Generate random patient data
            gender = random.choice(['M', 'F'])
            if gender == 'M':
                first_names = ['John', 'James', 'Michael', 'David', 'Robert', 'Peter', 'Kevin', 'Daniel', 'Samuel', 'Joseph']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
            else:
                first_names = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']

            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            # Generate valid phone number (max 15 characters)
            # Format: 07XXXXXXXXX (11 characters)
            phone = f"07{random.randint(10000000, 99999999)}"  # 11 characters total
            emergency_phone = f"07{random.randint(10000000, 99999999)}"

            # Generate valid email (max length)
            email = f"{first_name.lower()}.{last_name.lower()}@email.com"
            if len(email) > 100:
                email = f"{first_name[0].lower()}{last_name.lower()}@email.com"

            # Generate address
            address = f"{random.randint(1, 999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Maple Dr', 'Cedar Ln', 'Park Blvd', 'Lake Dr', 'Hill Rd'])}"

            # Create a patient
            try:
                patient = Patient.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=datetime(
                        random.randint(1940, 2005),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ).date(),
                    gender=gender,
                    phone_number=phone,
                    email=email,
                    address=address,
                    emergency_contact_name=f"{random.choice(['Mr.', 'Mrs.', 'Ms.'])} {random.choice(last_names)}",
                    emergency_contact_phone=emergency_phone,
                    created_by=doctor,
                    primary_physician=doctor,
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating patient: {e}'))
                continue

            # Create visit with "with_doctor" status (already in queue)
            visit_number = f"VIS-{datetime.now().strftime('%Y%m%d')}-{i+1:04d}"
            visit = PatientVisit.objects.create(
                patient=patient,
                visit_type=random.choice(['new', 'followup', 'emergency']),
                visit_number=visit_number,
                status='with_doctor',  # Already in doctor queue
                arrival_time=datetime.now() - timedelta(minutes=random.randint(5, 45)),
                doctor=doctor,
                created_by=doctor,
            )

            # Create triage record
            priority = random.choice(['emergency', 'urgent', 'semi_urgent', 'non_urgent'])
            TriageRecord.objects.create(
                visit=visit,
                patient=patient,
                temperature=round(random.uniform(36.0, 39.5), 1),
                heart_rate=random.randint(60, 120),
                respiratory_rate=random.randint(12, 25),
                blood_pressure_systolic=random.randint(100, 160),
                blood_pressure_diastolic=random.randint(60, 100),
                oxygen_saturation=random.randint(92, 99),
                weight=round(random.uniform(50, 120), 2),
                height=round(random.uniform(150, 190), 2),
                chief_complaint=random.choice(symptoms),
                priority=priority,
                allergies=random.choice(['None', 'Penicillin', 'Sulfa drugs', 'Latex', 'Peanuts', '']),
                current_medications=random.choice(['None', 'Paracetamol', 'Amoxicillin', 'Metformin', '']),
                triage_nurse=triage_nurse,
                is_completed=True,
                completed_at=datetime.now() - timedelta(minutes=random.randint(1, 15)),
            )

            patients_added += 1
            self.stdout.write(f'  Added: {patient.full_name} - {visit.visit_number} ({priority})')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'✅ {patients_added} patients added to queue!'))
        self.stdout.write('=' * 50)
        self.stdout.write('')
        self.stdout.write(f'  👨‍⚕️ Doctor: {doctor.get_full_name()}')
        self.stdout.write(f'  📋 Queue: {PatientVisit.objects.filter(status="with_doctor").count()} patients waiting')
        self.stdout.write('')
        self.stdout.write('  🔗 Go to: http://localhost:8000/doctor/')
        self.stdout.write('=' * 50)