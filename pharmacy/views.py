from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import app_role_required
from .forms import DispenseForm, MedicineForm
from .models import Medicine, Prescription


def pharmacy_stats():
    today = timezone.localdate()
    medicines = Medicine.objects.filter(is_active=True)
    return {
        'pending_count': Prescription.objects.filter(status='pending').count(),
        'urgent_count': Prescription.objects.filter(status='pending', priority='urgent').count(),
        'dispensed_today': Prescription.objects.filter(
            dispensed_at__date=today,
            status__in=('dispensed', 'awaiting_payment', 'paid'),
        ).count(),
        'low_stock_count': medicines.filter(quantity__lte=db_models.F('reorder_level')).count(),
        'awaiting_payment': Prescription.objects.filter(status='awaiting_payment').count(),
        'total_medicines': medicines.count(),
    }


@login_required
@app_role_required('pharmacy')
def dashboard(request):
    stats = pharmacy_stats()
    recent_prescriptions = Prescription.objects.filter(status='pending')[:5]
    low_stock = Medicine.objects.filter(
        is_active=True,
        quantity__lte=db_models.F('reorder_level'),
    )[:5]
    context = {
        'user': request.user,
        'stats': stats,
        'recent_prescriptions': recent_prescriptions,
        'low_stock': low_stock,
    }
    return render(request, 'pharmacy/dashboard.html', context)


@login_required
@app_role_required('pharmacy')
def prescription_list(request):
    status = request.GET.get('status', 'pending')
    prescriptions = Prescription.objects.all()
    if status and status != 'all':
        prescriptions = prescriptions.filter(status=status)
    context = {
        'prescriptions': prescriptions,
        'current_status': status,
        'status_choices': Prescription.STATUS_CHOICES,
    }
    return render(request, 'pharmacy/prescription_list.html', context)


@login_required
@app_role_required('pharmacy')
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    form = DispenseForm()
    if request.method == 'POST' and prescription.status == 'pending':
        form = DispenseForm(request.POST)
        if form.is_valid():
            for item in prescription.items.select_related('medicine'):
                if item.medicine and item.medicine.quantity < item.quantity:
                    messages.error(
                        request,
                        f'Insufficient stock for {item.medicine_name}. '
                        f'Available: {item.medicine.quantity}, needed: {item.quantity}.',
                    )
                    return redirect('pharmacy:prescription_detail', pk=pk)
            for item in prescription.items.select_related('medicine'):
                if item.medicine:
                    item.medicine.quantity -= item.quantity
                    item.medicine.save(update_fields=['quantity', 'updated_at'])
            prescription.status = (
                'awaiting_payment' if form.cleaned_data['send_to_payment'] else 'dispensed'
            )
            prescription.dispensed_by = request.user
            prescription.dispensed_at = timezone.now()
            if form.cleaned_data['notes']:
                prescription.notes = form.cleaned_data['notes']
            prescription.save()
            messages.success(
                request,
                f'Prescription for {prescription.patient_name} dispensed successfully.',
            )
            return redirect('pharmacy:prescription_list')
    context = {
        'prescription': prescription,
        'form': form,
    }
    return render(request, 'pharmacy/prescription_detail.html', context)


@login_required
@app_role_required('pharmacy')
def stock_list(request):
    medicines = Medicine.objects.all()
    low_stock_only = request.GET.get('low_stock') == '1'
    if low_stock_only:
        medicines = medicines.filter(quantity__lte=db_models.F('reorder_level'))
    context = {
        'medicines': medicines,
        'low_stock_only': low_stock_only,
    }
    return render(request, 'pharmacy/stock_list.html', context)


@login_required
@app_role_required('pharmacy')
def stock_add(request):
    form = MedicineForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{form.instance.name} added to stock.')
        return redirect('pharmacy:stock_list')
    return render(request, 'pharmacy/stock_form.html', {'form': form, 'title': 'Add Medicine'})


@login_required
@app_role_required('pharmacy')
def stock_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=medicine)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{medicine.name} updated.')
        return redirect('pharmacy:stock_list')
    return render(request, 'pharmacy/stock_form.html', {
        'form': form,
        'title': f'Edit {medicine.name}',
        'medicine': medicine,
    })
