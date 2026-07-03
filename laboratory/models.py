from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientVisit
from doctors.models import LabOrder, ImagingOrder
from datetime import datetime
from django.utils import timezone

User = get_user_model()


class LabResult(models.Model):
    """Lab test results"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('clarification_needed', 'Clarification Needed'),
        ('clarification_responded', 'Clarification Responded'),
    )
    
    lab_order = models.OneToOneField(LabOrder, on_delete=models.CASCADE, related_name='result')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='lab_results')
    
    # Results
    results = models.TextField(blank=True, help_text="Test results")
    result_date = models.DateTimeField(null=True, blank=True)
    result_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    
    # Notes
    technician_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True, help_text="Doctor's notes about the results")
    
    # Clarification
    clarification_request = models.TextField(blank=True, help_text="Lab technician's clarification request")
    clarification_response = models.TextField(blank=True, help_text="Doctor's response")
    clarification_requested_at = models.DateTimeField(null=True, blank=True)
    clarification_responded_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='performed_lab_results',
                                   limit_choices_to={'role': 'lab'})
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.lab_order.test_name} - {self.patient.full_name}"
    
    def start_test(self, technician):
        """Start processing the test"""
        self.status = 'in_progress'
        self.technician = technician
        self.save()
    
    def complete_test(self, results, notes=None):
        """Complete the test with results"""
        self.results = results
        self.result_date = timezone.now()
        self.completed_at = timezone.now()
        self.status = 'completed'
        if notes:
            self.technician_notes = notes
        self.save()
        
        # Update the lab order status
        self.lab_order.status = 'completed'
        self.lab_order.results = results
        self.lab_order.result_date = timezone.now()
        self.lab_order.technician = self.technician
        self.lab_order.completed_at = timezone.now()
        self.lab_order.save()
    
    def request_clarification(self, message):
        """Request clarification from doctor"""
        self.status = 'clarification_needed'
        self.clarification_request = message
        self.clarification_requested_at = timezone.now()
        self.save()
    
    def respond_to_clarification(self, response):
        """Doctor responds to clarification request"""
        self.status = 'clarification_responded'
        self.clarification_response = response
        self.clarification_responded_at = timezone.now()
        self.save()
    
    def cancel_test(self):
        """Cancel the test"""
        self.status = 'cancelled'
        self.lab_order.status = 'cancelled'
        self.lab_order.save()
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'lab_results'


class ImagingResult(models.Model):
    """Imaging test results"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('clarification_needed', 'Clarification Needed'),
        ('clarification_responded', 'Clarification Responded'),
    )
    
    imaging_order = models.OneToOneField(ImagingOrder, on_delete=models.CASCADE, related_name='result')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='imaging_results')
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='imaging_results')
    
    # Results
    findings = models.TextField(blank=True, help_text="Findings from imaging")
    impressions = models.TextField(blank=True, help_text="Impressions")
    result_date = models.DateTimeField(null=True, blank=True)
    result_file = models.FileField(upload_to='imaging_results/', blank=True, null=True)
    
    # Notes
    technician_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True, help_text="Doctor's notes about the results")
    
    # Clarification
    clarification_request = models.TextField(blank=True, help_text="Technician's clarification request")
    clarification_response = models.TextField(blank=True, help_text="Doctor's response")
    clarification_requested_at = models.DateTimeField(null=True, blank=True)
    clarification_responded_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='performed_imaging_results',
                                   limit_choices_to={'role': 'lab'})
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.imaging_order.get_imaging_type_display()} - {self.patient.full_name}"
    
    def start_test(self, technician):
        """Start processing the test"""
        self.status = 'in_progress'
        self.technician = technician
        self.save()
    
    def complete_test(self, findings, impressions, notes=None):
        """Complete the test with results"""
        self.findings = findings
        self.impressions = impressions
        self.result_date = timezone.now()
        self.completed_at = timezone.now()
        self.status = 'completed'
        if notes:
            self.technician_notes = notes
        self.save()
        
        # Update the imaging order
        self.imaging_order.findings = findings
        self.imaging_order.impressions = impressions
        self.imaging_order.result_date = timezone.now()
        self.imaging_order.technician = self.technician
        self.imaging_order.completed_at = timezone.now()
        self.imaging_order.save()
    
    def request_clarification(self, message):
        """Request clarification from doctor"""
        self.status = 'clarification_needed'
        self.clarification_request = message
        self.clarification_requested_at = timezone.now()
        self.save()
    
    def respond_to_clarification(self, response):
        """Doctor responds to clarification request"""
        self.status = 'clarification_responded'
        self.clarification_response = response
        self.clarification_responded_at = timezone.now()
        self.save()
    
    def cancel_test(self):
        """Cancel the test"""
        self.status = 'cancelled'
        self.imaging_order.status = 'cancelled'
        self.imaging_order.save()
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'imaging_results'