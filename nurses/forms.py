from django import forms
from .models import NurseNote, MedicationAdministration, PatientObservation


class NurseNoteForm(forms.ModelForm):
    """Form for nurse notes"""
    
    class Meta:
        model = NurseNote
        fields = ['note', 'is_feedback', 'feedback_type']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter your notes...'}),
            'feedback_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Medication reaction, Vitals change, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feedback_type'].required = False
        self.fields['feedback_type'].widget.attrs.update({'placeholder': 'Type of feedback (optional)'})


class MedicationAdministrationForm(forms.ModelForm):
    """Form for administering medication"""
    
    class Meta:
        model = MedicationAdministration
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any notes about administration...'}),
        }


class PatientObservationForm(forms.ModelForm):
    """Form for patient observations"""
    
    class Meta:
        model = PatientObservation
        fields = ['observation_type', 'description', 'is_urgent']
        widgets = {
            'observation_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe your observation...'}),
        }