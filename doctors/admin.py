from django.contrib import admin
from .models import MedicalRecord, Prescription, LabOrder, ImagingOrder

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'is_admitted', 'is_completed', 'created_at')
    list_filter = ('is_admitted', 'is_completed', 'ml_used', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'diagnosis')
    readonly_fields = ('created_at', 'updated_at', 'days_of_stay')
    
    fieldsets = (
        ('Patient & Doctor', {
            'fields': ('patient', 'visit', 'triage', 'doctor')
        }),
        ('Symptoms & Diagnosis', {
            'fields': ('symptoms', 'symptom_duration', 'symptom_severity', 
                      'clinical_notes', 'diagnosis', 'diagnosis_code', 
                      'differential_diagnosis')
        }),
        ('ML Assistance', {
            'fields': ('ml_suggestion', 'ml_confidence', 'ml_medication_suggestions', 'ml_used'),
            'classes': ('collapse',)
        }),
        ('Treatment & Follow-up', {
            'fields': ('treatment_plan', 'follow_up_date', 'follow_up_instructions')
        }),
        ('Admission & Discharge', {
            'fields': ('is_admitted', 'admission_date', 'discharge_date', 'days_of_stay')
        }),
        ('Referrals', {
            'fields': ('referred_to_lab', 'referred_to_imaging', 'referred_to_specialist', 'referral_notes')
        }),
        ('Status', {
            'fields': ('is_completed', 'completed_at')
        }),
    )

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medication_name', 'patient', 'doctor', 'status', 'created_at')
    list_filter = ('status', 'route', 'created_at')
    search_fields = ('medication_name', 'patient__first_name', 'patient__last_name')

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'patient', 'doctor', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'test_type', 'created_at')
    search_fields = ('test_name', 'patient__first_name', 'patient__last_name')

@admin.register(ImagingOrder)
class ImagingOrderAdmin(admin.ModelAdmin):
    list_display = ('imaging_type', 'body_part', 'patient', 'doctor', 'status', 'created_at')
    list_filter = ('status', 'imaging_type', 'priority', 'created_at')
    search_fields = ('body_part', 'patient__first_name', 'patient__last_name')