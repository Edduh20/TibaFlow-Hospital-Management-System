from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientVisit
from triage.models import TriageRecord
from datetime import date, datetime
from django.utils import timezone

User = get_user_model()

# ❌ DO NOT import from .models here - this causes circular import
# ✅ Remove this line if it exists:
# from .models import MedicalRecord, Prescription, LabOrder, ImagingOrder


class MedicalRecord(models.Model):
    """Complete medical record for a patient visit with workflow support"""
    
    PRIORITY_CHOICES = (
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    )
    
    WORKFLOW_STATUS = (
        ('draft', 'Draft - Initial Assessment'),
        ('prescribed', 'Prescribed - Waiting for Pharmacy'),
        ('lab_ordered', 'Lab Tests Ordered - Waiting for Results'),
        ('imaging_ordered', 'Imaging Ordered - Waiting for Results'),
        ('lab_imaging_ordered', 'Lab & Imaging Ordered - Waiting for Results'),
        ('nursing_care', 'Nursing Care - Sent to Nurse'),
        ('completed', 'Completed - All Done'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic Info
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='medical_records')
    triage = models.ForeignKey(TriageRecord, on_delete=models.SET_NULL, 
                               null=True, related_name='medical_records')
    doctor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='medical_records',
        limit_choices_to={'role': 'doctor'}
    )
    
    # Symptoms
    symptoms = models.TextField(help_text="Patient's reported symptoms")
    symptom_duration = models.CharField(max_length=100, blank=True)
    symptom_severity = models.IntegerField(
        choices=[(i, i) for i in range(1, 11)], 
        default=5
    )
    clinical_notes = models.TextField(blank=True, help_text="Doctor's clinical observations")
    
    # Diagnosis
    diagnosis = models.TextField(blank=True)
    diagnosis_code = models.CharField(max_length=50, blank=True)
    differential_diagnosis = models.TextField(blank=True)
    
    # ML Assistance
    ml_suggestion = models.TextField(blank=True)
    ml_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ml_medication_suggestions = models.TextField(blank=True)
    ml_used = models.BooleanField(default=False)
    
    # Treatment
    treatment_plan = models.TextField(blank=True)
    
    # Referrals
    referred_to_lab = models.BooleanField(default=False)
    referred_to_imaging = models.BooleanField(default=False)
    referred_to_specialist = models.BooleanField(default=False)
    referral_notes = models.TextField(blank=True)
    
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
    
    # Inpatient tracking
    is_admitted = models.BooleanField(default=False)
    admission_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    days_of_stay = models.IntegerField(default=0)
    
    # Workflow Status
    workflow_status = models.CharField(max_length=30, choices=WORKFLOW_STATUS, default='draft')
    is_locked = models.BooleanField(default=False, help_text="Locked when waiting for lab/imaging results")
    lock_reason = models.CharField(max_length=255, blank=True, help_text="Why is this record locked?")
    
    # Nursing Care
    needs_nursing_care = models.BooleanField(default=False)
    nursing_instructions = models.TextField(blank=True)
    nursing_completed = models.BooleanField(default=False)
    nursing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Medical Record for {self.patient.full_name} - {self.visit.visit_number}"
    
    def save(self, *args, **kwargs):
        if self.is_admitted and self.admission_date:
            if self.discharge_date:
                delta = self.discharge_date - self.admission_date
            else:
                delta = timezone.now() - self.admission_date
            self.days_of_stay = delta.days
        else:
            self.days_of_stay = 0
        super().save(*args, **kwargs)
    
    @property
    def current_days_of_stay(self):
        if self.is_admitted and self.admission_date:
            if self.discharge_date:
                delta = self.discharge_date - self.admission_date
            else:
                delta = timezone.now() - self.admission_date
            return delta.days
        return 0
    
    # ========== WORKFLOW METHODS ==========
    
    def lock_record(self, reason):
        """Lock the record so no edits can be made"""
        self.is_locked = True
        self.lock_reason = reason
        self.save()
    
    def unlock_record(self):
        """Unlock the record for editing"""
        self.is_locked = False
        self.lock_reason = ''
        self.save()
    
    def order_lab_tests(self):
        """Order lab tests - lock record and move patient to lab status"""
        self.referred_to_lab = True
        self.workflow_status = 'lab_ordered'
        self.lock_record('Waiting for lab test results')
        
        # Update visit status - remove from doctor's queue
        self.visit.status = 'lab'
        self.visit.save()
        self.save()
    
    def order_imaging(self):
        """Order imaging - lock record and move patient to lab status"""
        self.referred_to_imaging = True
        self.workflow_status = 'imaging_ordered'
        self.lock_record('Waiting for imaging results')
        
        # Update visit status - remove from doctor's queue
        self.visit.status = 'lab'
        self.visit.save()
        self.save()
    
    def order_both_lab_imaging(self):
        """Order both lab and imaging - lock record and move patient to lab status"""
        self.referred_to_lab = True
        self.referred_to_imaging = True
        self.workflow_status = 'lab_imaging_ordered'
        self.lock_record('Waiting for lab and imaging results')
        
        # Update visit status - remove from doctor's queue
        self.visit.status = 'lab'
        self.visit.save()
        self.save()
    
    def receive_lab_results(self):
        """Process lab results - unlock and return patient to queue with priority"""
        # Update visit status - put back in doctor's queue
        self.visit.status = 'with_doctor'
        self.visit.return_from_lab = True
        self.visit.is_priority_return = True
        self.visit.save()
        
        if self.referred_to_imaging:
            # Still waiting for imaging
            self.workflow_status = 'imaging_ordered'
            self.lock_reason = 'Waiting for imaging results'
        else:
            # All tests done
            self.workflow_status = 'draft'
            self.unlock_record()
        self.save()
    
    def receive_imaging_results(self):
        """Process imaging results - unlock and return patient to queue with priority"""
        # Update visit status - put back in doctor's queue
        self.visit.status = 'with_doctor'
        self.visit.return_from_imaging = True
        self.visit.is_priority_return = True
        self.visit.save()
        
        if self.referred_to_lab:
            # Still waiting for lab
            self.workflow_status = 'lab_ordered'
            self.lock_reason = 'Waiting for lab test results'
        else:
            # All tests done
            self.workflow_status = 'draft'
            self.unlock_record()
        self.save()
    
    def receive_both_results(self):
        """Process both lab and imaging results - unlock and return patient to queue with priority"""
        # Update visit status - put back in doctor's queue
        self.visit.status = 'with_doctor'
        self.visit.return_from_lab = True
        self.visit.return_from_imaging = True
        self.visit.is_priority_return = True
        self.visit.save()
        
        # All tests done
        self.workflow_status = 'draft'
        self.unlock_record()
        self.save()
    
    def send_to_pharmacy(self):
        """Send prescription to pharmacy"""
        self.workflow_status = 'prescribed'
        self.save()
    
    def send_to_nurse(self, instructions):
        """Send patient to nurse for care"""
        self.workflow_status = 'nursing_care'
        self.needs_nursing_care = True
        self.nursing_instructions = instructions
        self.lock_record('Patient sent to nurse for care')
        self.save()
    
    def complete_nursing_care(self):
        """Nurse completes care"""
        self.nursing_completed = True
        self.nursing_completed_at = timezone.now()
        self.unlock_record()
        self.workflow_status = 'draft'
        self.save()
    
    def complete_record(self):
        """Mark the entire record as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.workflow_status = 'completed'
        self.unlock_record()
        self.save()
    
    def cancel_record(self):
        """Cancel the record"""
        self.workflow_status = 'cancelled'
        self.unlock_record()
        self.save()
    
    def cancel_lab_tests(self):
        """Cancel lab tests and return patient to queue"""
        self.referred_to_lab = False
        self.workflow_status = 'draft'
        self.unlock_record()
        
        # Return to doctor's queue
        self.visit.status = 'with_doctor'
        self.visit.is_priority_return = False
        self.visit.return_from_lab = False
        self.visit.save()
        self.save()
    
    def cancel_imaging(self):
        """Cancel imaging and return patient to queue"""
        self.referred_to_imaging = False
        self.workflow_status = 'draft'
        self.unlock_record()
        
        # Return to doctor's queue
        self.visit.status = 'with_doctor'
        self.visit.is_priority_return = False
        self.visit.return_from_imaging = False
        self.visit.save()
        self.save()
    
    @property
    def can_edit(self):
        """Check if doctor can edit this record"""
        return not self.is_locked and not self.is_completed
    
    @property
    def can_complete(self):
        """Check if record can be completed"""
        return not self.is_locked and not self.is_completed and self.workflow_status in ['draft', 'prescribed']
    
    @property
    def is_waiting_for_lab(self):
        """Check if waiting for lab results"""
        return self.workflow_status in ['lab_ordered', 'lab_imaging_ordered']
    
    @property
    def is_waiting_for_imaging(self):
        """Check if waiting for imaging results"""
        return self.workflow_status in ['imaging_ordered', 'lab_imaging_ordered']
    
    @property
    def is_with_nurse(self):
        """Check if with nurse for care"""
        return self.workflow_status == 'nursing_care'
    
    @property
    def display_status(self):
        """Get display status for templates"""
        status_map = {
            'draft': ('secondary', 'In Progress'),
            'prescribed': ('info', 'Prescribed'),
            'lab_ordered': ('warning', 'Lab Tests'),
            'imaging_ordered': ('warning', 'Imaging'),
            'lab_imaging_ordered': ('warning', 'Lab & Imaging'),
            'nursing_care': ('primary', 'With Nurse'),
            'completed': ('success', 'Completed'),
            'cancelled': ('danger', 'Cancelled'),
        }
        return status_map.get(self.workflow_status, ('secondary', 'Unknown'))
    
    class Meta:
        ordering = ['-created_at']


class Prescription(models.Model):
    """Medication prescription"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled'),
    )
    
    ROUTE_CHOICES = (
        ('oral', 'Oral'),
        ('iv', 'Intravenous'),
        ('im', 'Intramuscular'),
        ('subcutaneous', 'Subcutaneous'),
        ('topical', 'Topical'),
        ('inhalation', 'Inhalation'),
        ('rectal', 'Rectal'),
        ('other', 'Other'),
    )
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescriptions', limit_choices_to={'role': 'doctor'})
    
    medication_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=50, help_text="e.g., 500mg")
    frequency = models.CharField(max_length=100, help_text="e.g., 2x daily")
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES, default='oral')
    duration = models.CharField(max_length=50, help_text="e.g., 7 days")
    quantity = models.IntegerField(help_text="Total quantity to dispense")
    refills = models.IntegerField(default=0, help_text="Number of refills allowed")
    instructions = models.TextField(blank=True, help_text="Special instructions for patient")
    
    pharmacist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispensed_prescriptions', limit_choices_to={'role': 'pharmacy'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    dispensed_at = models.DateTimeField(null=True, blank=True)
    dispensed_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription: {self.medication_name} for {self.patient.full_name}"
    
    def approve(self):
        self.status = 'approved'
        self.save()
    
    def dispense(self, pharmacist):
        self.status = 'dispensed'
        self.pharmacist = pharmacist
        self.dispensed_at = datetime.now()
        self.save()


class LabOrder(models.Model):
    """Lab test orders from doctor"""
    
    PRIORITY_CHOICES = (
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    )
    
    STATUS_CHOICES = (
        ('ordered', 'Ordered'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_orders')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_orders')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordered_lab_tests', limit_choices_to={'role': 'doctor'})
    
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=50, help_text="Blood, Urine, Stool, etc.")
    clinical_notes = models.TextField(blank=True, help_text="What to look for")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    
    results = models.TextField(blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    result_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_lab_tests', limit_choices_to={'role': 'lab'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    
    needs_clarification = models.BooleanField(default=False)
    clarification_request = models.TextField(blank=True)
    clarification_response = models.TextField(blank=True)
    clarification_requested_at = models.DateTimeField(null=True, blank=True)
    clarification_responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name}"
    
    def mark_completed(self, technician, results):
        self.status = 'completed'
        self.technician = technician
        self.results = results
        self.result_date = datetime.now()
        self.completed_at = datetime.now()
        self.save()
    
    def request_clarification(self, message):
        self.needs_clarification = True
        self.clarification_request = message
        self.clarification_requested_at = datetime.now()
        self.status = 'pending'
        self.save()
    
    def respond_to_clarification(self, response):
        self.needs_clarification = False
        self.clarification_response = response
        self.clarification_responded_at = datetime.now()
        self.status = 'in_progress'
        self.save()


class ImagingOrder(models.Model):
    """Imaging orders from doctor"""
    
    IMAGING_TYPES = (
        ('xray', 'X-Ray'),
        ('ct', 'CT Scan'),
        ('mri', 'MRI'),
        ('ultrasound', 'Ultrasound'),
        ('pet', 'PET Scan'),
        ('ecg', 'ECG/EKG'),
        ('other', 'Other'),
    )
    
    PRIORITY_CHOICES = (
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    )
    
    STATUS_CHOICES = (
        ('ordered', 'Ordered'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='imaging_orders')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='imaging_orders')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordered_imaging', limit_choices_to={'role': 'doctor'})
    
    imaging_type = models.CharField(max_length=20, choices=IMAGING_TYPES)
    body_part = models.CharField(max_length=100)
    clinical_indication = models.TextField(help_text="Why this imaging is needed")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    
    findings = models.TextField(blank=True)
    impressions = models.TextField(blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    result_file = models.FileField(upload_to='imaging_results/', blank=True, null=True)
    
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_imaging', limit_choices_to={'role': 'lab'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    
    needs_clarification = models.BooleanField(default=False)
    clarification_request = models.TextField(blank=True)
    clarification_response = models.TextField(blank=True)
    clarification_requested_at = models.DateTimeField(null=True, blank=True)
    clarification_responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_imaging_type_display()} of {self.body_part} - {self.patient.full_name}"
    
    def request_clarification(self, message):
        self.needs_clarification = True
        self.clarification_request = message
        self.clarification_requested_at = datetime.now()
        self.status = 'pending'
        self.save()
    
    def respond_to_clarification(self, response):
        self.needs_clarification = False
        self.clarification_response = response
        self.clarification_responded_at = datetime.now()
        self.status = 'in_progress'
        self.save()