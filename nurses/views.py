from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from patients.models import Patient, PatientVisit
from doctors.models import Prescription, MedicalRecord
from triage.models import TriageRecord
from .models import NurseNote, MedicationAdministration, PatientObservation
from .forms import NurseNoteForm, MedicationAdministrationForm, PatientObservationForm


@login_required
def nurse_dashboard(request):
    """Nurse dashboard with assigned patients"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    today = timezone.now().date()
    
    # Get admitted patients (limited view for nurses)
    admitted_patients = Patient.objects.filter(
        is_admitted=True
    ).order_by('-admission_date')
    
    # Get patients needing nursing care from triage
    nursing_care_patients = TriageRecord.objects.filter(
        status='nursing_care',
        nursing_care_completed=False
    ).order_by('created_at')
    
    # Get patients with pending medications
    pending_medications = MedicationAdministration.objects.filter(
        status='pending'
    ).order_by('created_at')
    
    # Get recent observations
    recent_observations = PatientObservation.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:10]
    
    # Get patients with prescriptions to administer
    prescriptions_today = Prescription.objects.filter(
        created_at__date=today
    ).count()
    
    context = {
        'admitted_patients': admitted_patients[:10],
        'admitted_count': admitted_patients.count(),
        'nursing_care_patients': nursing_care_patients[:10],
        'nursing_care_count': nursing_care_patients.count(),
        'pending_medications': pending_medications[:10],
        'pending_medications_count': pending_medications.count(),
        'recent_observations': recent_observations,
        'prescriptions_today': prescriptions_today,
    }
    return render(request, 'nurses/dashboard.html', context)


@login_required
def patient_detail(request, patient_id):
    """View patient details (limited access)"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Check if patient is admitted or assigned to nurse
    # For now, allow viewing any patient
    
    # Get prescriptions for this patient
    prescriptions = Prescription.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    # Get triage records for days of stay
    triage_records = TriageRecord.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    # Get nurse notes
    nurse_notes = NurseNote.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    # Get medication administrations
    medication_administrations = MedicationAdministration.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    # Get medical records (doctor's notes)
    medical_records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'triage_records': triage_records,
        'nurse_notes': nurse_notes,
        'medication_administrations': medication_administrations,
        'medical_records': medical_records,
    }
    return render(request, 'nurses/patient_detail.html', context)


@login_required
def add_nurse_note(request, patient_id):
    """Add a note for a patient"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        form = NurseNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.patient = patient
            note.created_by = request.user
            note.save()
            
            if note.is_feedback:
                messages.success(request, f'Feedback sent to doctor for {patient.full_name}')
            else:
                messages.success(request, f'Note added for {patient.full_name}')
            
            return redirect('nurses:patient_detail', patient_id=patient.id)
    else:
        form = NurseNoteForm()
    
    context = {
        'patient': patient,
        'form': form,
    }
    return render(request, 'nurses/add_note.html', context)


@login_required
def administer_medication(request, patient_id, prescription_id):
    """Administer medication to patient"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    patient = get_object_or_404(Patient, id=patient_id)
    prescription = get_object_or_404(Prescription, id=prescription_id, patient=patient)
    
    # Get or create medication administration record
    admin_record, created = MedicationAdministration.objects.get_or_create(
        patient=patient,
        prescription=prescription,
        defaults={'status': 'pending'}
    )
    
    if request.method == 'POST':
        form = MedicationAdministrationForm(request.POST, instance=admin_record)
        if form.is_valid():
            admin_record = form.save(commit=False)
            admin_record.administered_by = request.user
            admin_record.save()
            
            messages.success(request, f'Medication {prescription.medication_name} administered to {patient.full_name}')
            return redirect('nurses:patient_detail', patient_id=patient.id)
    else:
        form = MedicationAdministrationForm(instance=admin_record)
    
    context = {
        'patient': patient,
        'prescription': prescription,
        'admin_record': admin_record,
        'form': form,
    }
    return render(request, 'nurses/administer_medication.html', context)


@login_required
def add_observation(request, patient_id):
    """Add patient observation"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        form = PatientObservationForm(request.POST)
        if form.is_valid():
            observation = form.save(commit=False)
            observation.patient = patient
            observation.created_by = request.user
            observation.save()
            
            if observation.is_urgent:
                messages.warning(request, f'⚠️ Urgent observation recorded for {patient.full_name}')
            else:
                messages.success(request, f'Observation recorded for {patient.full_name}')
            
            return redirect('nurses:patient_detail', patient_id=patient.id)
    else:
        form = PatientObservationForm()
    
    context = {
        'patient': patient,
        'form': form,
    }
    return render(request, 'nurses/add_observation.html', context)


@login_required
def nursing_care_patients(request):
    """View patients needing nursing care"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    nursing_patients = TriageRecord.objects.filter(
        status='nursing_care',
        nursing_care_completed=False
    ).order_by('created_at')
    
    paginator = Paginator(nursing_patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'nursing_patients': page_obj,
    }
    return render(request, 'nurses/nursing_care_list.html', context)


@login_required
def pending_medications(request):
    """View all pending medications"""
    if request.user.role not in ['nurse', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    pending = MedicationAdministration.objects.filter(
        status='pending'
    ).order_by('created_at')
    
    paginator = Paginator(pending, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_medications': page_obj,
    }
    return render(request, 'nurses/pending_medications.html', context)


@login_required
def get_stats(request):
    """AJAX endpoint for nurse stats"""
    if request.user.role not in ['nurse', 'admin']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    stats = {
        'admitted': Patient.objects.filter(is_admitted=True).count(),
        'nursing_care': TriageRecord.objects.filter(
            status='nursing_care',
            nursing_care_completed=False
        ).count(),
        'pending_medications': MedicationAdministration.objects.filter(status='pending').count(),
        'observations_today': PatientObservation.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)