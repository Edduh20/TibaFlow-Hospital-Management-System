from django.contrib import admin
from .models import TriageRecord

@admin.register(TriageRecord)
class TriageRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'visit', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'visit__visit_number')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'sent_to_doctor_at')
    
    fieldsets = (
        ('Patient & Visit', {
            'fields': ('patient', 'visit')
        }),
        ('Vitals', {
            'fields': ('temperature', 'heart_rate', 'respiratory_rate', 
                      'blood_pressure_systolic', 'blood_pressure_diastolic',
                      'oxygen_saturation', 'weight', 'height')
        }),
        ('Assessment', {
            'fields': ('chief_complaint', 'priority', 'allergies', 
                      'current_medications', 'medical_history')
        }),
        ('Nursing Care', {
            'fields': ('needs_nursing_care', 'nursing_instructions', 
                      'nursing_notes', 'nursing_care_completed', 
                      'nursing_care_completed_at')
        }),
        ('Status', {
            'fields': ('status', 'is_completed', 'completed_at', 'sent_to_doctor_at')
        }),
        ('Metadata', {
            'fields': ('triage_nurse', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )