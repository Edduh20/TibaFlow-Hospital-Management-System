from django import forms
from django.contrib.auth import get_user_model
from .models import Patient

User = get_user_model()


class PatientForm(forms.ModelForm):
    """Form for creating and editing patients"""
    
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'blood_type', 'email', 'phone_number', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'allergies', 'chronic_conditions', 'previous_surgeries',
            'current_medications', 'family_medical_history', 'medical_history_notes',
            'insurance_type', 'insurance_number', 'insurance_expiry',
            'primary_physician'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'List all allergies'}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Chronic conditions...'}),
            'previous_surgeries': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Previous surgeries...'}),
            'current_medications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Current medications...'}),
            'family_medical_history': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Family medical history...'}),
            'medical_history_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Additional notes...'}),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        return phone