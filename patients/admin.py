from django.contrib import admin
from .models import Patient, PatientVisit, Payment

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'email', 'age', 'is_admitted', 'visit_count', 'created_at')
    list_filter = ('gender', 'is_admitted', 'insurance_type', 'status')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email')
    readonly_fields = ('created_at', 'updated_at', 'visit_count')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Medical History', {
            'fields': ('allergies', 'chronic_conditions', 'previous_surgeries', 'current_medications', 
                      'family_medical_history', 'medical_history_notes'),
            'classes': ('collapse',)
        }),
        ('Insurance', {
            'fields': ('insurance_type', 'insurance_number', 'insurance_expiry')
        }),
        ('Admission', {
            'fields': ('is_admitted', 'admission_date', 'discharge_date', 'room_number', 'bed_number')
        }),
        ('Status', {
            'fields': ('status', 'visit_count', 'last_visit_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'primary_physician'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = ('visit_number', 'patient', 'visit_type', 'status', 'arrival_time')
    list_filter = ('status', 'visit_type', 'arrival_time')
    search_fields = ('visit_number', 'patient__first_name', 'patient__last_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'patient', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('receipt_number', 'patient__first_name', 'patient__last_name')