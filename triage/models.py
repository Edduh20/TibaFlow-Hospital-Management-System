from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientVisit
from datetime import datetime
from django.utils import timezone

User = get_user_model()


class TriageRecord(models.Model):
    PRIORITY_CHOICES = (
        ('emergency', 'Emergency'),
        ('urgent', 'Urgent'),
        ('semi_urgent', 'Semi-Urgent'),
        ('non_urgent', 'Non-Urgent'),
    )
    
    VISIT_STATUS = (
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('sent_to_doctor', 'Sent to Doctor'),
        ('nursing_care', 'Nursing Care'),
        ('completed_care', 'Completed Care'),
    )
    
    visit = models.OneToOneField(PatientVisit, on_delete=models.CASCADE, related_name='triage')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='triage_records')
    
    # Vitals
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    respiratory_rate = models.IntegerField(null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    oxygen_saturation = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Triage Assessment
    chief_complaint = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='non_urgent')
    allergies = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    
    # Nursing Care
    needs_nursing_care = models.BooleanField(default=False)
    nursing_instructions = models.TextField(blank=True, help_text="Instructions from doctor for nursing care")
    nursing_notes = models.TextField(blank=True, help_text="Notes from nurse")
    nursing_care_completed = models.BooleanField(default=False)
    nursing_care_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Nurse Notes
    nurse_notes = models.TextField(blank=True)
    triage_nurse = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                     null=True, related_name='triage_records',
                                     limit_choices_to={'role__in': ['triage', 'nurse']})
    
    # Status
    status = models.CharField(max_length=20, choices=VISIT_STATUS, default='waiting')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    sent_to_doctor_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Triage for {self.patient.full_name} - {self.visit.visit_number}"
    
    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = self.height / 100
            return self.weight / (height_m ** 2)
        return None
    
    def send_to_doctor(self):
        """Send patient to doctor"""
        self.status = 'sent_to_doctor'
        self.is_completed = True
        self.completed_at = timezone.now()
        self.sent_to_doctor_at = timezone.now()
        self.visit.status = 'with_doctor'
        self.visit.save()
        self.save()
    
    def receive_from_doctor(self, instructions):
        """Receive patient from doctor for nursing care"""
        self.status = 'nursing_care'
        self.needs_nursing_care = True
        self.nursing_instructions = instructions
        self.save()
    
    def complete_nursing_care(self, notes=None):
        """Complete nursing care"""
        self.nursing_care_completed = True
        self.nursing_care_completed_at = timezone.now()
        self.status = 'completed_care'
        if notes:
            self.nursing_notes = notes
        self.save()
    
    def complete_triage(self):
        """Complete triage assessment"""
        self.status = 'completed'
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'triage_records'