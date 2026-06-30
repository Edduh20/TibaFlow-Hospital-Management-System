from django.db import models
from django.contrib.auth import get_user_model
from datetime import date, datetime

User = get_user_model()


class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    INSURANCE_CHOICES = (
        ('nhif', 'NHIF'),
        ('private', 'Private Insurance'),
        ('none', 'None'),
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    
    # Medical Information
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_CHOICES, default='none')
    insurance_number = models.CharField(max_length=50, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    
    # Visit Information
    visit_count = models.IntegerField(default=0)
    last_visit_date = models.DateTimeField(null=True, blank=True)
    is_admitted = models.BooleanField(default=False)
    admission_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    room_number = models.CharField(max_length=10, blank=True)
    bed_number = models.CharField(max_length=10, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                   null=True, related_name='created_patients')
    primary_physician = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                          null=True, blank=True, related_name='patients',
                                          limit_choices_to={'role': 'doctor'})
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def days_of_stay(self):
        if self.is_admitted and self.admission_date:
            if self.discharge_date:
                delta = self.discharge_date - self.admission_date
            else:
                delta = datetime.now() - self.admission_date
            return delta.days
        return 0
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']


class PatientVisit(models.Model):
    VISIT_STATUS = (
        ('pending', 'Pending'),
        ('triage', 'At Triage'),
        ('with_doctor', 'With Doctor'),
        ('lab', 'Lab Tests'),
        ('pharmacy', 'At Pharmacy'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    VISIT_TYPE = (
        ('new', 'New Patient'),
        ('followup', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('referral', 'Referral'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE, default='new')
    visit_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=VISIT_STATUS, default='pending')
    
    # Timestamps
    arrival_time = models.DateTimeField(auto_now_add=True)
    triage_time = models.DateTimeField(null=True, blank=True)
    doctor_time = models.DateTimeField(null=True, blank=True)
    discharge_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    
    # Referral Information
    referral_from = models.CharField(max_length=100, blank=True)
    referral_to = models.CharField(max_length=100, blank=True)
    referral_notes = models.TextField(blank=True)
    
    # Payment Information
    payment_verified = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Doctor assignment
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='assigned_visits',
                               limit_choices_to={'role': 'doctor'})
    
    # Queue Management (NEW FIELDS)
    queue_position = models.IntegerField(default=0, help_text="Position in doctor's queue")
    is_priority_return = models.BooleanField(default=False, help_text="True if returning from lab/imaging - goes to front of queue")
    return_from_lab = models.BooleanField(default=False, help_text="True if returning from lab")
    return_from_imaging = models.BooleanField(default=False, help_text="True if returning from imaging")
    lab_ordered = models.BooleanField(default=False, help_text="True if lab tests were ordered")
    imaging_ordered = models.BooleanField(default=False, help_text="True if imaging was ordered")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                   null=True, related_name='created_visits')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.visit_number} - {self.patient.full_name}"
    
    def mark_as_priority_return(self):
        """Mark this visit as a priority return (front of queue)"""
        self.is_priority_return = True
        self.queue_position = 0
        self.save()
    
    def remove_priority(self):
        """Remove priority status after being seen"""
        self.is_priority_return = False
        self.queue_position = 0
        self.return_from_lab = False
        self.return_from_imaging = False
        self.save()
    
    def send_to_lab(self):
        """Send patient to lab"""
        self.status = 'lab'
        self.lab_ordered = True
        self.save()
    
    def send_to_pharmacy(self):
        """Send patient to pharmacy"""
        self.status = 'pharmacy'
        self.save()
    
    def return_from_lab_to_doctor(self):
        """Return from lab to doctor's queue (front of line)"""
        self.status = 'with_doctor'
        self.return_from_lab = True
        self.is_priority_return = True
        self.queue_position = 0
        self.save()
    
    def return_from_imaging_to_doctor(self):
        """Return from imaging to doctor's queue (front of line)"""
        self.status = 'with_doctor'
        self.return_from_imaging = True
        self.is_priority_return = True
        self.queue_position = 0
        self.save()
    
    def complete_visit(self):
        """Mark visit as completed"""
        self.status = 'completed'
        self.completed_time = datetime.now()
        self.is_priority_return = False
        self.save()
    
    class Meta:
        db_table = 'patient_visits'
        ordering = ['-created_at']


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('insurance', 'Insurance'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='payments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']