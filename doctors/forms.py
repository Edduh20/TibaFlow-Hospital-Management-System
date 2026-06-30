from django import forms
from .models import MedicalRecord, Prescription, LabOrder, ImagingOrder

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'symptoms', 'symptom_duration', 'symptom_severity',
            'clinical_notes', 'diagnosis', 'diagnosis_code',
            'differential_diagnosis', 'treatment_plan',
            'ml_suggestion', 'ml_confidence', 'ml_medication_suggestions',
            'follow_up_date', 'follow_up_instructions',
            'is_admitted', 'referral_notes'
        ]
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 3}),
            'clinical_notes': forms.Textarea(attrs={'rows': 3}),
            'diagnosis': forms.Textarea(attrs={'rows': 2}),
            'differential_diagnosis': forms.Textarea(attrs={'rows': 2}),
            'treatment_plan': forms.Textarea(attrs={'rows': 3}),
            'ml_suggestion': forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}),
            'ml_medication_suggestions': forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
            'referral_notes': forms.Textarea(attrs={'rows': 2}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            'medication_name', 'generic_name', 'dosage',
            'frequency', 'route', 'duration', 'quantity',
            'refills', 'instructions'
        ]
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }

class LabOrderForm(forms.ModelForm):
    class Meta:
        model = LabOrder
        fields = ['test_name', 'test_type', 'clinical_notes', 'priority']
        widgets = {
            'clinical_notes': forms.Textarea(attrs={'rows': 2}),
        }

class ImagingOrderForm(forms.ModelForm):
    class Meta:
        model = ImagingOrder
        fields = ['imaging_type', 'body_part', 'clinical_indication', 'priority']
        widgets = {
            'clinical_indication': forms.Textarea(attrs={'rows': 2}),
        }

class DischargeForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['follow_up_instructions', 'referral_notes']
        widgets = {
            'follow_up_instructions': forms.Textarea(attrs={'rows': 2}),
            'referral_notes': forms.Textarea(attrs={'rows': 2}),
        }