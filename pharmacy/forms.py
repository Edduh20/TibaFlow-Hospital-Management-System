from django import forms

from .models import Medicine, Prescription


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = (
            'name', 'generic_name', 'quantity', 'unit',
            'reorder_level', 'expiry_date', 'is_active',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DispenseForm(forms.Form):
    send_to_payment = forms.BooleanField(
        required=False,
        initial=True,
        label='Send to payment counter after dispensing',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
