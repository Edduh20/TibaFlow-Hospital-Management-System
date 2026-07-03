from django.contrib import admin
from .models import LabResult, ImagingResult

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'lab_order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'lab_order__test_name')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

@admin.register(ImagingResult)
class ImagingResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'imaging_order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'imaging_order__body_part')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')