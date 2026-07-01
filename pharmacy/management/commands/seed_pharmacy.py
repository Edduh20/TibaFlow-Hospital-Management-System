from datetime import date, timedelta

from django.core.management.base import BaseCommand

from pharmacy.models import Medicine, Prescription, PrescriptionItem

# name, generic_name, category, qty, unit, reorder, location, supplier, expiry_days (None = no expiry)
INVENTORY_ITEMS = [
    # Medicines
    ('Paracetamol 500mg', 'Acetaminophen', 'medicine', 120, 'tablets', 30, 'Pharmacy Shelf A1', 'PharmaCare Ltd', 180),
    ('Amoxicillin 250mg', 'Amoxicillin', 'medicine', 80, 'capsules', 20, 'Pharmacy Shelf A2', 'PharmaCare Ltd', 365),
    ('Ibuprofen 400mg', 'Ibuprofen', 'medicine', 15, 'tablets', 25, 'Pharmacy Shelf A1', 'MediSupply Co', 120),
    ('Cetirizine 10mg', 'Cetirizine', 'medicine', 60, 'tablets', 15, 'Pharmacy Shelf B1', 'PharmaCare Ltd', 240),
    ('ORS Sachets', 'Oral rehydration salts', 'medicine', 45, 'units', 20, 'Pharmacy Shelf C2', 'HealthPack Kenya', 90),
    ('Metformin 500mg', 'Metformin', 'medicine', 200, 'tablets', 40, 'Pharmacy Shelf A3', 'PharmaCare Ltd', 365),
    ('Amlodipine 5mg', 'Amlodipine', 'medicine', 90, 'tablets', 25, 'Pharmacy Shelf A3', 'MediSupply Co', 300),
    ('Azithromycin 250mg', 'Azithromycin', 'medicine', 8, 'tablets', 20, 'Pharmacy Shelf B2', 'PharmaCare Ltd', 180),
    ('Salbutamol Inhaler', 'Salbutamol', 'medicine', 22, 'units', 10, 'Pharmacy Fridge', 'RespiraMed', 365),
    ('Insulin Glargine', 'Insulin glargine', 'medicine', 12, 'vials', 8, 'Pharmacy Cold Room', 'DiabetesCare Ltd', 90),
    ('Artemether-Lumefantrine', 'Coartem', 'medicine', 35, 'tablets', 15, 'Pharmacy Shelf B3', 'MalariaPharm', 200),
    ('Omeprazole 20mg', 'Omeprazole', 'medicine', 5, 'capsules', 20, 'Pharmacy Shelf A2', 'MediSupply Co', 150),
    # Medical supplies
    ('Surgical Gloves (L)', 'Nitrile examination gloves', 'supply', 500, 'units', 100, 'Store Room S1', 'SurgiPro Supplies', 730),
    ('Disposable Syringes 5ml', 'Sterile syringes', 'supply', 300, 'units', 80, 'Store Room S1', 'SurgiPro Supplies', 1095),
    ('IV Cannula 22G', 'Peripheral IV cannula', 'supply', 150, 'units', 40, 'Ward Store W2', 'SurgiPro Supplies', 1095),
    ('Gauze Bandage Roll', 'Sterile gauze', 'supply', 80, 'units', 25, 'Store Room S2', 'HealthPack Kenya', 365),
    ('Alcohol Swabs', 'Isopropyl alcohol pads', 'supply', 12, 'units', 30, 'Store Room S2', 'HealthPack Kenya', 180),
    ('Face Masks (Surgical)', '3-ply surgical masks', 'supply', 400, 'units', 100, 'Store Room S3', 'SafeGuard Medical', 365),
    ('Cotton Wool 500g', 'Absorbent cotton', 'supply', 25, 'units', 10, 'Store Room S2', 'HealthPack Kenya', None),
    ('Urine Collection Bags', 'Adult urine bag', 'supply', 60, 'units', 20, 'Ward Store W1', 'CareLine Supplies', 730),
    ('Suture Kit', 'Absorbable suture set', 'supply', 18, 'units', 8, 'Theatre Store T1', 'SurgiPro Supplies', 1095),
    ('Blood Collection Tubes', 'EDTA vacutainer', 'supply', 200, 'units', 50, 'Lab Store L1', 'LabTech Supplies', 365),
    # Equipment
    ('Digital BP Monitor', 'Automatic blood pressure monitor', 'equipment', 6, 'units', 2, 'Equipment Room E1', 'MedEquip Africa', None),
    ('Pulse Oximeter', 'Finger pulse oximeter', 'equipment', 10, 'units', 3, 'Equipment Room E1', 'MedEquip Africa', None),
    ('Wheelchair Standard', 'Folding patient wheelchair', 'equipment', 4, 'units', 1, 'Equipment Bay', 'Mobility Solutions', None),
    ('Nebulizer Machine', 'Compressor nebulizer', 'equipment', 3, 'units', 1, 'Equipment Room E2', 'RespiraMed', None),
    ('Hospital Bed (Manual)', 'Adjustable manual bed', 'equipment', 2, 'units', 1, 'Ward Storage', 'HospiFurn Ltd', None),
    ('Defibrillator (AED)', 'Automated external defibrillator', 'equipment', 1, 'units', 1, 'Emergency Bay', 'CardioTech', None),
    ('Infusion Pump', 'Volumetric infusion pump', 'equipment', 5, 'units', 2, 'ICU Equipment', 'MedEquip Africa', None),
    ('Glucometer Kit', 'Blood glucose monitoring kit', 'equipment', 8, 'units', 2, 'Equipment Room E1', 'DiabetesCare Ltd', None),
    ('Stethoscope (Dual Head)', 'Clinical stethoscope', 'equipment', 7, 'units', 2, 'Equipment Room E1', 'MedEquip Africa', None),
    ('Oxygen Concentrator', '5L oxygen concentrator', 'equipment', 2, 'units', 1, 'Equipment Room E2', 'RespiraMed', None),
]


class Command(BaseCommand):
    help = 'Load sample inventory items, medicines, and prescriptions for pharmacy preview'

    def handle(self, *args, **options):
        medicines = {}
        for row in INVENTORY_ITEMS:
            name, generic, category, qty, unit, reorder, location, supplier, expiry_days = row
            defaults = {
                'generic_name': generic,
                'category': category,
                'quantity': qty,
                'unit': unit,
                'reorder_level': reorder,
                'storage_location': location,
                'supplier': supplier,
                'expiry_date': date.today() + timedelta(days=expiry_days) if expiry_days else None,
                'is_active': True,
            }
            item, created = Medicine.objects.update_or_create(name=name, defaults=defaults)
            medicines[name] = item
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action}: {name} ({category})')

        if Prescription.objects.exists():
            self.stdout.write(self.style.WARNING('Prescriptions already exist — skipping sample prescriptions.'))
            self.stdout.write(self.style.SUCCESS(f'Inventory seed complete — {len(INVENTORY_ITEMS)} items.'))
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

        rx4 = Prescription.objects.create(
            patient_name='James Wilson',
            patient_age=52,
            status='pending',
            priority='normal',
        )
        PrescriptionItem.objects.create(
            prescription=rx4,
            medicine=medicines['Metformin 500mg'],
            medicine_name='Metformin 500mg',
            dosage='500mg',
            frequency='2 times daily',
            duration='30 days',
            quantity=60,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Sample data loaded — {len(INVENTORY_ITEMS)} inventory items and 4 prescriptions.'
        ))
