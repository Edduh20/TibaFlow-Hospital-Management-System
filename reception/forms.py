from django import forms
from patients.models import Patient, PatientVisit
from django.contrib.auth import get_user_model
from .models import InsuranceVerification

User = get_user_model()


class PatientRegistrationForm(forms.ModelForm):
    """Form for registering a new patient"""
    
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'blood_type', 'email', 'phone_number', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'insurance_type', 'insurance_number', 'insurance_expiry'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter emergency contact name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter emergency contact phone'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter insurance policy number'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'insurance_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        return phone


class VisitRegistrationForm(forms.ModelForm):
    """Form for creating a new visit"""
    
    class Meta:
        model = PatientVisit
        fields = ['visit_type', 'referral_from', 'referral_to', 'referral_notes']
        widgets = {
            'visit_type': forms.Select(attrs={'class': 'form-control'}),
            'referral_from': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referring hospital/clinic'}),
            'referral_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referred to'}),
            'referral_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Referral notes...'}),
        }


class InsuranceVerificationForm(forms.ModelForm):
    """Form for verifying insurance"""
    
    class Meta:
        model = InsuranceVerification
        fields = ['insurance_company', 'policy_number', 'member_name', 'relationship', 'notes']
        widgets = {
            'insurance_company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insurance company name'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Policy number'}),
            'member_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Member name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship to member'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Verification notes...'}),
        }