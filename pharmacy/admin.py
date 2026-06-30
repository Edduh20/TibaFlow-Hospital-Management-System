from django.contrib import admin

from .models import Medicine, Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'quantity', 'unit', 'reorder_level', 'is_active')
    list_filter = ('is_active', 'unit')
    search_fields = ('name', 'generic_name')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_age', 'status', 'priority', 'prescribed_by', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('patient_name',)
    inlines = [PrescriptionItemInline]
