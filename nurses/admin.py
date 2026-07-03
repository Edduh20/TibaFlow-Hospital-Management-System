from django.contrib import admin
from .models import NurseNote, MedicationAdministration, PatientObservation

@admin.register(NurseNote)
class NurseNoteAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_by', 'is_feedback', 'created_at')
    list_filter = ('is_feedback', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'note')
    readonly_fields = ('created_at',)

@admin.register(MedicationAdministration)
class MedicationAdministrationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'prescription', 'status', 'administered_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'prescription__medication_name')

@admin.register(PatientObservation)
class PatientObservationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'observation_type', 'is_urgent', 'created_at')
    list_filter = ('observation_type', 'is_urgent', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'description')