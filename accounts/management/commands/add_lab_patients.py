from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from patients.models import Patient, PatientVisit
from triage.models import TriageRecord
from doctors.models import MedicalRecord, LabOrder, ImagingOrder

User = get_user_model()


class Command(BaseCommand):
    help = 'Add patients who need lab and imaging services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of patients to add (default: 5)',
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
            help='Clear existing lab patients before adding new ones',
        )

    def generate_unique_visit_number(self):
        """Generate a unique visit number"""
        today = datetime.now().strftime('%Y%m%d')
        
        # Get all visit numbers for today
        existing_numbers = PatientVisit.objects.filter(
            visit_number__startswith=f'VIS-{today}-'
        ).values_list('visit_number', flat=True)
        
        # Find the next available number
        counter = 1
        while True:
            visit_number = f"VIS-{today}-{counter:04d}"
            if visit_number not in existing_numbers:
                return visit_number
            counter += 1

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
            # Clear existing lab and imaging orders
            LabOrder.objects.all().delete()
            ImagingOrder.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing lab/imaging orders.'))

        self.stdout.write(f'Adding {count} patients needing lab/imaging services...')

        # Common symptoms and tests
        symptoms_list = [
            'Fever, cough, and body aches',
            'Headache and dizziness',
            'Stomach pain and nausea',
            'Chest pain and shortness of breath',
            'Joint pain and swelling',
            'Skin rash and itching',
            'Sore throat and difficulty swallowing',
            'Back pain and muscle stiffness',
            'Fatigue and weakness',
            'Ear pain and discharge',
            'Eye redness and discharge',
            'Dental pain and swelling',
            'Vomiting and diarrhea',
            'Urinary pain and frequency',
            'Weight loss and appetite loss'
        ]

        lab_tests = [
            ('Complete Blood Count', 'Blood'),
            ('Urinalysis', 'Urine'),
            ('Blood Glucose', 'Blood'),
            ('Lipid Profile', 'Blood'),
            ('Liver Function Test', 'Blood'),
            ('Kidney Function Test', 'Blood'),
            ('Thyroid Function Test', 'Blood'),
            ('Stool Culture', 'Stool'),
            ('Blood Culture', 'Blood'),
            ('Pregnancy Test', 'Blood'),
            ('HIV Test', 'Blood'),
            ('Malaria Test', 'Blood'),
            ('Dengue Test', 'Blood'),
            ('Urine Culture', 'Urine'),
            ('Hormone Test', 'Blood'),
        ]

        imaging_tests = [
            ('xray', 'Chest'),
            ('xray', 'Knee'),
            ('xray', 'Hand'),
            ('xray', 'Foot'),
            ('xray', 'Spine'),
            ('xray', 'Pelvis'),
            ('ct', 'Head'),
            ('ct', 'Chest'),
            ('ct', 'Abdomen'),
            ('mri', 'Brain'),
            ('mri', 'Knee'),
            ('ultrasound', 'Abdomen'),
            ('ultrasound', 'Pelvis'),
            ('ultrasound', 'Heart'),
            ('ecg', 'Heart'),
        ]

        patients_added = 0

        for i in range(count):
            try:
                # Generate random patient
                gender = random.choice(['M', 'F'])
                if gender == 'M':
                    first_names = ['John', 'James', 'Michael', 'David', 'Robert', 'Peter', 'Kevin', 'Daniel', 'Samuel', 'Joseph']
                    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
                else:
                    first_names = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
                    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']

                first_name = random.choice(first_names)
                last_name = random.choice(last_names)

                # Generate phone number
                phone = f"07{random.randint(10000000, 99999999)}"
                emergency_phone = f"07{random.randint(10000000, 99999999)}"

                # Create patient
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
                    email=f"{first_name.lower()}.{last_name.lower()}@email.com",
                    address=f"{random.randint(1, 999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Maple Dr', 'Cedar Ln', 'Park Blvd'])}",
                    emergency_contact_name=f"{random.choice(['Mr.', 'Mrs.', 'Ms.'])} {random.choice(last_names)}",
                    emergency_contact_phone=emergency_phone,
                    insurance_type=random.choice(['nhif', 'private', 'none']),
                    created_by=doctor,
                    primary_physician=doctor,
                )

                # Generate unique visit number
                visit_number = self.generate_unique_visit_number()
                
                # Create visit
                visit = PatientVisit.objects.create(
                    patient=patient,
                    visit_type=random.choice(['new', 'followup', 'emergency']),
                    visit_number=visit_number,
                    status='lab',  # Directly set to lab status
                    arrival_time=timezone.now() - timedelta(hours=random.randint(1, 4)),
                    doctor=doctor,
                    created_by=doctor,
                )

                # Create triage record
                symptoms = random.choice(symptoms_list)
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
                    chief_complaint=symptoms,
                    priority=priority,
                    allergies=random.choice(['None', 'Penicillin', 'Sulfa drugs', 'Latex', 'Peanuts']),
                    current_medications=random.choice(['None', 'Paracetamol', 'Amoxicillin', 'Metformin']),
                    triage_nurse=triage_nurse,
                    is_completed=True,
                    completed_at=timezone.now() - timedelta(hours=1),
                )

                # Create medical record
                record = MedicalRecord.objects.create(
                    patient=patient,
                    visit=visit,
                    triage=TriageRecord.objects.get(visit=visit),
                    symptoms=symptoms,
                    symptom_duration=f"{random.randint(1, 14)} days",
                    symptom_severity=random.randint(1, 10),
                    clinical_notes=f"Patient presents with {symptoms.lower()}",
                    diagnosis="Under investigation - tests ordered",
                    treatment_plan="Awaiting lab/imaging results",
                    doctor=doctor,
                    is_admitted=random.choice([True, False]),
                    is_completed=False,  # Not completed yet - waiting for tests
                    created_at=timezone.now() - timedelta(hours=1),
                )

                # Determine if lab, imaging, or both
                test_type = random.choice(['lab', 'imaging', 'both'])

                if test_type == 'lab' or test_type == 'both':
                    # Add lab tests
                    num_tests = random.randint(1, 3)
                    for _ in range(num_tests):
                        test_name, test_type_choice = random.choice(lab_tests)
                        LabOrder.objects.create(
                            medical_record=record,
                            patient=patient,
                            doctor=doctor,
                            test_name=test_name,
                            test_type=test_type_choice,
                            clinical_notes=f"Test ordered for {symptoms.lower()}",
                            priority=random.choice(['routine', 'urgent', 'emergency']),
                            status='ordered',  # Waiting for lab to process
                            created_at=timezone.now() - timedelta(minutes=random.randint(10, 30)),
                        )

                    self.stdout.write(f'  ✅ Added lab tests for {patient.full_name}')

                if test_type == 'imaging' or test_type == 'both':
                    # Add imaging tests
                    num_tests = random.randint(1, 2)
                    for _ in range(num_tests):
                        imaging_type, body_part = random.choice(imaging_tests)
                        ImagingOrder.objects.create(
                            medical_record=record,
                            patient=patient,
                            doctor=doctor,
                            imaging_type=imaging_type,
                            body_part=body_part,
                            clinical_indication=f"Imaging needed for {symptoms.lower()}",
                            priority=random.choice(['routine', 'urgent', 'emergency']),
                            status='ordered',  # Waiting for lab to process
                            created_at=timezone.now() - timedelta(minutes=random.randint(5, 15)),
                        )

                    self.stdout.write(f'  ✅ Added imaging tests for {patient.full_name}')

                patients_added += 1
                self.stdout.write(f'  ✅ Patient {patient.full_name} sent to lab/imaging')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating patient: {e}'))
                continue

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'✅ {patients_added} patients added with lab/imaging orders!'))
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write(f'  👨‍⚕️ Doctor: {doctor.get_full_name()}')
        self.stdout.write(f'  🧪 Lab Orders: {LabOrder.objects.filter(status="ordered").count()}')
        self.stdout.write(f'  📷 Imaging Orders: {ImagingOrder.objects.filter(status="ordered").count()}')
        self.stdout.write(f'  🏥 Patients in Lab Queue: {PatientVisit.objects.filter(status="lab").count()}')
        self.stdout.write('')
        self.stdout.write('  🔗 Go to Laboratory Dashboard: http://127.0.0.1:8000/lab/')
        self.stdout.write('=' * 60)