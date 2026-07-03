from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import csv

from .models import Patient, PatientVisit, Payment
from doctors.models import MedicalRecord, Prescription, LabOrder, ImagingOrder
from .forms import PatientForm


def get_role_access_level(user):
    """Determine what patient data a user can see based on role"""
    if user.role == 'reception':
        return 'full'  # All info
    elif user.role == 'doctor':
        return 'doctor'  # All except payment
    elif user.role == 'triage':
        return 'triage'  # Limited (name, age, visit)
    elif user.role == 'nurse':
        return 'nurse'  # Limited (name, age, prescription, days of stay)
    else:
        return 'limited'


@login_required
def patient_list(request):
    """List all patients with search and filters"""
    patients = Patient.objects.all()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        patients = patients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'admitted':
            patients = patients.filter(is_admitted=True)
        elif status_filter == 'discharged':
            patients = patients.filter(status='discharged')
        elif status_filter == 'referred':
            patients = patients.filter(status='referred')
        else:
            patients = patients.filter(status='active')
    
    insurance_filter = request.GET.get('insurance', '')
    if insurance_filter:
        patients = patients.filter(insurance_type=insurance_filter)
    
    # Sort
    sort = request.GET.get('sort', '-created_at')
    patients = patients.order_by(sort)
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics for admin/reception
    stats = {}
    if request.user.role in ['reception', 'admin']:
        stats = {
            'total': Patient.objects.count(),
            'admitted': Patient.objects.filter(is_admitted=True).count(),
            'active': Patient.objects.filter(status='active').count(),
            'discharged': Patient.objects.filter(status='discharged').count(),
        }
    
    context = {
        'patients': page_obj,
        'search': search,
        'status_filter': status_filter,
        'insurance_filter': insurance_filter,
        'stats': stats,
        'access_level': get_role_access_level(request.user),
    }
    return render(request, 'patients/list.html', context)


@login_required
def patient_detail(request, patient_id):
    """View patient details with role-based access control"""
    patient = get_object_or_404(Patient, id=patient_id)
    access_level = get_role_access_level(request.user)
    
    # Get related data
    visits = patient.visits.all().order_by('-created_at')[:10]
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')[:5]
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')[:5]
    payments = patient.payments.all().order_by('-payment_date')[:5]
    
    context = {
        'patient': patient,
        'access_level': access_level,
        'visits': visits,
        'medical_records': medical_records,
        'prescriptions': prescriptions,
        'payments': payments,
    }
    
    # Add role-specific data
    if access_level == 'full' or access_level == 'doctor':
        context['lab_orders'] = LabOrder.objects.filter(patient=patient).order_by('-created_at')[:5]
        context['imaging_orders'] = ImagingOrder.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    return render(request, 'patients/detail.html', context)


@login_required
def patient_create(request):
    """Create a new patient (Reception and Admin only)"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Only receptionists and admins can create patients.')
        return redirect('patients:list')
    
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            messages.success(request, f'Patient {patient.full_name} created successfully!')
            return redirect('patients:detail', patient_id=patient.id)
    else:
        form = PatientForm()
    
    context = {'form': form}
    return render(request, 'patients/create.html', context)


@login_required
def patient_edit(request, patient_id):
    """Edit patient details (Reception and Admin only)"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Only receptionists and admins can edit patients.')
        return redirect('patients:list')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient {patient.full_name} updated successfully!')
            return redirect('patients:detail', patient_id=patient.id)
    else:
        form = PatientForm(instance=patient)
    
    context = {'form': form, 'patient': patient}
    return render(request, 'patients/edit.html', context)


@login_required
def patient_delete(request, patient_id):
    """Soft delete a patient (Reception and Admin only)"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Only receptionists and admins can delete patients.')
        return redirect('patients:list')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        patient.status = 'inactive'
        patient.save()
        messages.success(request, f'Patient {patient.full_name} has been deactivated.')
        return redirect('patients:list')
    
    context = {'patient': patient}
    return render(request, 'patients/delete.html', context)


@login_required
def patient_admit(request, patient_id):
    """Admit a patient (Reception, Admin, and Doctors)"""
    if request.user.role not in ['reception', 'admin', 'doctor']:
        messages.error(request, 'Access denied.')
        return redirect('patients:list')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        room_number = request.POST.get('room_number', '')
        bed_number = request.POST.get('bed_number', '')
        patient.admit(room_number, bed_number)
        messages.success(request, f'Patient {patient.full_name} admitted successfully!')
        return redirect('patients:detail', patient_id=patient.id)
    
    context = {'patient': patient}
    return render(request, 'patients/admit.html', context)


@login_required
def patient_discharge(request, patient_id):
    """Discharge a patient (Reception, Admin, and Doctors)"""
    if request.user.role not in ['reception', 'admin', 'doctor']:
        messages.error(request, 'Access denied.')
        return redirect('patients:list')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        patient.discharge()
        messages.success(request, f'Patient {patient.full_name} discharged successfully!')
        return redirect('patients:detail', patient_id=patient.id)
    
    context = {'patient': patient}
    return render(request, 'patients/discharge.html', context)


@login_required
def patient_export(request):
    """Export patient list to CSV (Admin and Reception only)"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied.')
        return redirect('patients:list')
    
    # Get all patients
    patients = Patient.objects.all().order_by('-created_at')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="patients_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'First Name', 'Last Name', 'Age', 'Gender', 'Phone', 'Email',
        'Insurance Type', 'Status', 'Visit Count', 'Created At'
    ])
    
    for patient in patients:
        writer.writerow([
            patient.id,
            patient.first_name,
            patient.last_name,
            patient.age,
            patient.get_gender_display(),
            patient.phone_number,
            patient.email,
            patient.get_insurance_type_display(),
            patient.display_status,
            patient.visit_count,
            patient.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


@login_required
def get_patient_stats(request):
    """AJAX endpoint for patient statistics"""
    if request.user.role not in ['reception', 'admin']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    stats = {
        'total': Patient.objects.count(),
        'admitted': Patient.objects.filter(is_admitted=True).count(),
        'active': Patient.objects.filter(status='active').count(),
        'discharged': Patient.objects.filter(status='discharged').count(),
        'referred': Patient.objects.filter(status='referred').count(),
    }
    
    return JsonResponse(stats)


@login_required
def patient_medical_history(request, patient_id):
    """Get patient medical history (AJAX)"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    data = {
        'allergies': patient.allergies,
        'chronic_conditions': patient.chronic_conditions,
        'previous_surgeries': patient.previous_surgeries,
        'current_medications': patient.current_medications,
        'family_medical_history': patient.family_medical_history,
        'medical_history_notes': patient.medical_history_notes,
    }
    
    return JsonResponse(data)