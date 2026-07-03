from django.contrib import admin
from .models import ReceptionNote, InsuranceVerification

@admin.register(ReceptionNote)
class ReceptionNoteAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__first_name', 'patient__last_name', 'note')
    readonly_fields = ('created_at',)

@admin.register(InsuranceVerification)
class InsuranceVerificationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'insurance_company', 'policy_number', 'verification_status', 'verified_at')
    list_filter = ('verification_status', 'verified_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'insurance_company', 'policy_number')
    readonly_fields = ('created_at', 'verified_at')