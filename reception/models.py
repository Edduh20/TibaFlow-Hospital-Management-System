from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientVisit
from datetime import datetime

User = get_user_model()


class ReceptionNote(models.Model):
    """Notes for receptionists about patients"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reception_notes')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='reception_notes', null=True, blank=True)
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reception_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note for {self.patient.full_name} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-created_at']


class InsuranceVerification(models.Model):
    """Insurance verification records"""
    
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_verifications')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='insurance_verifications')
    insurance_company = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=50)
    member_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_insurances')
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.insurance_company}"
    
    def verify(self, user):
        self.verification_status = 'verified'
        self.verified_by = user
        self.verified_at = datetime.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']