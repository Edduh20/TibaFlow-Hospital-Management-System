from datetime import date, timedelta

from django.core.management.base import BaseCommand

from pharmacy.models import Medicine, Prescription, PrescriptionItem


class Command(BaseCommand):
    help = 'Load sample medicines and prescriptions for pharmacy preview'

    def handle(self, *args, **options):
        medicines_data = [
            ('Paracetamol 500mg', 'Acetaminophen', 120, 'tablets', 30),
            ('Amoxicillin 250mg', 'Amoxicillin', 80, 'capsules', 20),
            ('Ibuprofen 400mg', 'Ibuprofen', 15, 'tablets', 25),
            ('Cetirizine 10mg', 'Cetirizine', 60, 'tablets', 15),
            ('ORS Sachets', 'Oral rehydration salts', 45, 'units', 20),
        ]

        medicines = {}
        for name, generic, qty, unit, reorder in medicines_data:
            med, created = Medicine.objects.update_or_create(
                name=name,
                defaults={
                    'generic_name': generic,
                    'quantity': qty,
                    'unit': unit,
                    'reorder_level': reorder,
                    'expiry_date': date.today() + timedelta(days=180),
                    'is_active': True,
                },
            )
            medicines[name] = med
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} medicine: {name}')

        if Prescription.objects.exists():
            self.stdout.write(self.style.WARNING('Prescriptions already exist — skipping sample prescriptions.'))
            return

        rx1 = Prescription.objects.create(
            patient_name='Sarah Johnson',
            patient_age=34,
            status='pending',
            priority='urgent',
            notes='Take after meals.',
        )
        PrescriptionItem.objects.bulk_create([
            PrescriptionItem(
                prescription=rx1,
                medicine=medicines['Paracetamol 500mg'],
                medicine_name='Paracetamol 500mg',
                dosage='500mg',
                frequency='3 times daily',
                duration='5 days',
                quantity=15,
            ),
            PrescriptionItem(
                prescription=rx1,
                medicine=medicines['Amoxicillin 250mg'],
                medicine_name='Amoxicillin 250mg',
                dosage='250mg',
                frequency='2 times daily',
                duration='7 days',
                quantity=14,
            ),
        ])

        rx2 = Prescription.objects.create(
            patient_name='Michael Brown',
            patient_age=28,
            status='pending',
            priority='normal',
        )
        PrescriptionItem.objects.create(
            prescription=rx2,
            medicine=medicines['Ibuprofen 400mg'],
            medicine_name='Ibuprofen 400mg',
            dosage='400mg',
            frequency='As needed',
            duration='3 days',
            quantity=9,
        )

        rx3 = Prescription.objects.create(
            patient_name='Emily Davis',
            patient_age=45,
            status='awaiting_payment',
            priority='normal',
        )
        PrescriptionItem.objects.create(
            prescription=rx3,
            medicine=medicines['Cetirizine 10mg'],
            medicine_name='Cetirizine 10mg',
            dosage='10mg',
            frequency='Once daily',
            duration='10 days',
            quantity=10,
        )

        self.stdout.write(self.style.SUCCESS('Sample pharmacy data loaded successfully.'))
