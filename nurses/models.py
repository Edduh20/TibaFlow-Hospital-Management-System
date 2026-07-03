from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientVisit
from doctors.models import Prescription
from datetime import datetime
from django.utils import timezone

User = get_user_model()


class NurseNote(models.Model):
    """Notes from nurse about patient"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nurse_notes')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='nurse_notes')
    note = models.TextField()
    is_feedback = models.BooleanField(default=False, help_text="Is this feedback to the doctor?")
    feedback_type = models.CharField(max_length=50, blank=True, help_text="Type of feedback (e.g., medication reaction, vitals change, etc.)")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='nurse_notes', limit_choices_to={'role': 'nurse'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note for {self.patient.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'nurse_notes'


class MedicationAdministration(models.Model):
    """Record of medication administered by nurse"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('administered', 'Administered'),
        ('refused', 'Refused'),
        ('held', 'Held'),
        ('missed', 'Missed'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medication_administrations')
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='administrations')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='medication_administrations')
    
    administered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='administered_medications', limit_choices_to={'role': 'nurse'})
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.prescription.medication_name} - {self.patient.full_name}"
    
    def administer(self, user, notes=None):
        """Administer medication"""
        self.status = 'administered'
        self.administered_at = timezone.now()
        self.administered_by = user
        if notes:
            self.notes = notes
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'medication_administrations'


class PatientObservation(models.Model):
    """Patient observations recorded by nurse"""
    
    OBSERVATION_TYPES = (
        ('vitals', 'Vitals Check'),
        ('behavior', 'Behavior Change'),
        ('symptom', 'New Symptom'),
        ('improvement', 'Improvement'),
        ('deterioration', 'Deterioration'),
        ('other', 'Other'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='observations')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='observations')
    observation_type = models.CharField(max_length=20, choices=OBSERVATION_TYPES)
    description = models.TextField()
    is_urgent = models.BooleanField(default=False, help_text="Is this observation urgent?")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='observations', limit_choices_to={'role': 'nurse'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_observation_type_display()} - {self.patient.full_name}"
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'patient_observations'