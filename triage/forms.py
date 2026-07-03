from django import forms
from .models import TriageRecord
from patients.models import PatientVisit


class TriageForm(forms.ModelForm):
    """Form for triage assessment"""
    
    class Meta:
        model = TriageRecord
        fields = [
            'temperature', 'heart_rate', 'respiratory_rate',
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'oxygen_saturation', 'weight', 'height',
            'chief_complaint', 'priority',
            'allergies', 'current_medications', 'medical_history',
            'nurse_notes'
        ]
        widgets = {
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g., 36.5'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 72'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 16'}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 80'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 98'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 70.5'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 175'}),
            'chief_complaint': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'What is the patient\'s main complaint?'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Any allergies?'}),
            'current_medications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Current medications?'}),
            'medical_history': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Medical history...'}),
            'nurse_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Additional notes...'}),
        }


class NursingCareForm(forms.ModelForm):
    """Form for nursing care"""
    
    class Meta:
        model = TriageRecord
        fields = ['nursing_notes']
        widgets = {
            'nursing_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter nursing care notes...'}),
        }


class SendToDoctorForm(forms.Form):
    """Form for confirming send to doctor"""
    confirm = forms.BooleanField(required=True, widget=forms.HiddenInput, initial=True)


class ReceiveFromDoctorForm(forms.Form):
    """Form for receiving patient from doctor for nursing care"""
    nursing_instructions = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'class': 'form-control',
            'placeholder': 'Enter nursing care instructions from doctor...'
        }),
        label='Nursing Care Instructions',
        help_text='Instructions from the doctor for nursing care (e.g., injections, medication administration, etc.)'
    )