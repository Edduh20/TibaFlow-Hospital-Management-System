from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from patients.models import Patient, PatientVisit
from triage.models import TriageRecord
from .models import ReceptionNote, InsuranceVerification
from .forms import PatientRegistrationForm, VisitRegistrationForm, InsuranceVerificationForm

User = get_user_model()


@login_required
def reception_dashboard(request):
    """Reception dashboard with statistics and patient queue"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Statistics
    patients_today = PatientVisit.objects.filter(
        arrival_time__date=today
    ).count()
    
    pending_visits = PatientVisit.objects.filter(
        status='pending'
    ).count()
    
    total_patients = Patient.objects.count()
    
    # Patients waiting for triage
    waiting_for_triage = PatientVisit.objects.filter(
        status='pending'
    ).order_by('arrival_time')
    
    # Today's visits
    today_visits = PatientVisit.objects.filter(
        arrival_time__date=today
    ).order_by('-arrival_time')[:20]
    
    # Recent patients
    recent_patients = Patient.objects.order_by('-created_at')[:10]
    
    # Upcoming appointments (if any)
    upcoming_appointments = PatientVisit.objects.filter(
        arrival_time__gte=timezone.now(),
        status='pending'
    ).order_by('arrival_time')[:5]
    
    # Wait time estimates (avg wait time for today)
    completed_today = PatientVisit.objects.filter(
        arrival_time__date=today,
        status='completed'
    )
    avg_wait_time = 0
    if completed_today.exists():
        total_wait = 0
        for visit in completed_today:
            if visit.triage_time:
                wait = (visit.triage_time - visit.arrival_time).total_seconds() / 60
                total_wait += wait
        avg_wait_time = round(total_wait / completed_today.count())
    
    context = {
        'patients_today': patients_today,
        'pending_visits': pending_visits,
        'total_patients': total_patients,
        'waiting_for_triage': waiting_for_triage[:10],
        'waiting_count': waiting_for_triage.count(),
        'today_visits': today_visits,
        'recent_patients': recent_patients,
        'upcoming_appointments': upcoming_appointments,
        'avg_wait_time': avg_wait_time,
    }
    return render(request, 'reception/dashboard.html', context)


@login_required
def register_patient(request):
    """Register a new patient and create a visit"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        patient_form = PatientRegistrationForm(request.POST)
        visit_form = VisitRegistrationForm(request.POST)
        
        if patient_form.is_valid() and visit_form.is_valid():
            # Save patient
            patient = patient_form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            
            # Generate unique visit number
            today = timezone.now().strftime('%Y%m%d')
            
            # Get the last visit number for today
            last_visit = PatientVisit.objects.filter(
                visit_number__startswith=f'VIS-{today}-'
            ).order_by('-visit_number').first()
            
            if last_visit:
                # Extract the number and increment
                last_number = int(last_visit.visit_number.split('-')[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            
            visit_number = f"VIS-{today}-{next_number:04d}"
            
            # Save visit
            visit = visit_form.save(commit=False)
            visit.patient = patient
            visit.visit_number = visit_number
            visit.status = 'pending'  # Initial status
            visit.created_by = request.user
            visit.save()
            
            # Handle insurance verification if insurance is provided
            if patient.insurance_type != 'none' and patient.insurance_number:
                # Create insurance verification record
                InsuranceVerification.objects.create(
                    patient=patient,
                    visit=visit,
                    insurance_company=patient.get_insurance_type_display(),
                    policy_number=patient.insurance_number,
                    member_name=patient.full_name,
                    verification_status='pending',
                )
            
            messages.success(request, f'Patient {patient.full_name} registered successfully! Visit: {visit.visit_number}')
            
            # Check if we should send to triage
            if request.POST.get('send_to_triage'):
                return redirect('reception:send_to_triage', visit_id=visit.id)
            
            return redirect('reception:patient_detail', patient_id=patient.id)
    else:
        patient_form = PatientRegistrationForm()
        visit_form = VisitRegistrationForm()
    
    context = {
        'patient_form': patient_form,
        'visit_form': visit_form,
    }
    return render(request, 'reception/register_patient.html', context)


@login_required
def patient_detail(request, patient_id):
    """View patient details"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    patient = get_object_or_404(Patient, id=patient_id)
    visits = patient.visits.all().order_by('-created_at')
    insurance_verifications = patient.insurance_verifications.all().order_by('-created_at')
    
    context = {
        'patient': patient,
        'visits': visits,
        'insurance_verifications': insurance_verifications,
    }
    return render(request, 'reception/patient_detail.html', context)


@login_required
def patient_search(request):
    """Search for patients"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    query = request.GET.get('q', '')
    patients = []
    
    if query:
        patients = Patient.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query)
        ).order_by('-created_at')
    
    context = {
        'query': query,
        'patients': patients,
    }
    return render(request, 'reception/patient_search.html', context)


@login_required
def send_to_triage(request, visit_id):
    """Send a patient to triage"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    visit = get_object_or_404(PatientVisit, id=visit_id)
    
    if request.method == 'POST':
        # Update visit status
        visit.status = 'triage'
        visit.triage_time = timezone.now()
        visit.save()
        
        # Create triage record (empty, will be filled by triage nurse)
        TriageRecord.objects.create(
            visit=visit,
            patient=visit.patient,
            chief_complaint='',  # Will be filled by triage nurse
        )
        
        messages.success(request, f'Patient {visit.patient.full_name} sent to triage successfully!')
        return redirect('reception:dashboard')
    
    context = {
        'visit': visit,
        'patient': visit.patient,
    }
    return render(request, 'reception/send_to_triage.html', context)


@login_required
def verify_insurance(request, visit_id):
    """Verify patient insurance"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    visit = get_object_or_404(PatientVisit, id=visit_id)
    patient = visit.patient
    
    # Get or create insurance verification
    verification, created = InsuranceVerification.objects.get_or_create(
        patient=patient,
        visit=visit,
        defaults={
            'insurance_company': patient.get_insurance_type_display(),
            'policy_number': patient.insurance_number or '',
            'member_name': patient.full_name,
            'verification_status': 'pending',
        }
    )
    
    if request.method == 'POST':
        form = InsuranceVerificationForm(request.POST, instance=verification)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.verified_by = request.user
            verification.verified_at = timezone.now()
            
            # Check if manually verified
            if request.POST.get('manual_verify'):
                verification.verification_status = 'verified'
            else:
                verification.verification_status = 'pending'
            
            verification.save()
            
            # Update payment verification on visit
            if verification.verification_status == 'verified':
                visit.payment_verified = True
                visit.save()
            
            messages.success(request, f'Insurance verified for {patient.full_name}')
            return redirect('reception:patient_detail', patient_id=patient.id)
    else:
        form = InsuranceVerificationForm(instance=verification)
    
    context = {
        'form': form,
        'patient': patient,
        'visit': visit,
        'verification': verification,
    }
    return render(request, 'reception/verify_insurance.html', context)


@login_required
def patient_queue(request):
    """View patient queue"""
    if request.user.role not in ['reception', 'admin']:
        messages.error(request, 'Access denied. Receptionists only.')
        return redirect('core:dashboard')
    
    patients = PatientVisit.objects.filter(
        status__in=['pending', 'triage']
    ).order_by('arrival_time')
    
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patients': page_obj,
    }
    return render(request, 'reception/patient_queue.html', context)


@login_required
def get_quick_stats(request):
    """AJAX endpoint for quick stats"""
    if request.user.role not in ['reception', 'admin']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    today = timezone.now().date()
    
    stats = {
        'patients_today': PatientVisit.objects.filter(arrival_time__date=today).count(),
        'pending_visits': PatientVisit.objects.filter(status='pending').count(),
        'with_triage': PatientVisit.objects.filter(status='triage').count(),
        'with_doctor': PatientVisit.objects.filter(status='with_doctor').count(),
        'completed_today': PatientVisit.objects.filter(
            arrival_time__date=today,
            status='completed'
        ).count(),
        'total_patients': Patient.objects.count(),
    }
    
    return JsonResponse(stats)