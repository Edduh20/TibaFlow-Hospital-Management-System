from django import forms
from .models import LabResult, ImagingResult


class LabResultForm(forms.ModelForm):
    """Form for lab test results"""
    
    class Meta:
        model = LabResult
        fields = ['results', 'technician_notes', 'result_file']
        widgets = {
            'results': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Enter test results...'}),
            'technician_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any additional notes...'}),
            'result_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ImagingResultForm(forms.ModelForm):
    """Form for imaging test results"""
    
    class Meta:
        model = ImagingResult
        fields = ['findings', 'impressions', 'technician_notes', 'result_file']
        widgets = {
            'findings': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Enter findings...'}),
            'impressions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter impressions...'}),
            'technician_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any additional notes...'}),
            'result_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ClarificationForm(forms.Form):
    """Form for requesting clarification"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'What clarification do you need from the doctor?'
        }),
        label='Clarification Request'
    )


class ClarificationResponseForm(forms.Form):
    """Form for responding to clarification"""
    response = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Enter your response...'
        }),
        label='Response'
    )