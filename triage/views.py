from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from patients.models import Patient, PatientVisit
from .models import TriageRecord
from .forms import TriageForm, NursingCareForm, SendToDoctorForm


@login_required
def triage_dashboard(request):
    """Triage dashboard with patient queue"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        messages.error(request, 'Access denied. Triage nurses only.')
        return redirect('core:dashboard')
    
    # Get patients waiting for triage
    waiting_patients = PatientVisit.objects.filter(
        status='triage'
    ).order_by('arrival_time')
    
    # Get patients in triage (being assessed)
    in_progress = TriageRecord.objects.filter(
        status='in_progress'
    ).order_by('-created_at')
    
    # Get patients waiting for nursing care
    nursing_care = TriageRecord.objects.filter(
        status='nursing_care',
        nursing_care_completed=False
    ).order_by('created_at')
    
    # Get completed triage today
    completed_today = TriageRecord.objects.filter(
        completed_at__date=timezone.now().date()
    ).count()
    
    # Get patients sent to doctor today
    sent_to_doctor_today = TriageRecord.objects.filter(
        sent_to_doctor_at__date=timezone.now().date()
    ).count()
    
    context = {
        'waiting_patients': waiting_patients[:10],
        'waiting_count': waiting_patients.count(),
        'in_progress': in_progress[:10],
        'in_progress_count': in_progress.count(),
        'nursing_care': nursing_care[:10],
        'nursing_care_count': nursing_care.count(),
        'completed_today': completed_today,
        'sent_to_doctor_today': sent_to_doctor_today,
    }
    return render(request, 'triage/dashboard.html', context)


@login_required
def triage_patient(request, visit_id):
    """Triage a patient (limited view)"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        messages.error(request, 'Access denied. Triage nurses only.')
        return redirect('core:dashboard')
    
    visit = get_object_or_404(PatientVisit, id=visit_id, status='triage')
    patient = visit.patient
    
    # Get or create triage record
    triage, created = TriageRecord.objects.get_or_create(
        visit=visit,
        patient=patient,
        defaults={'status': 'in_progress'}
    )
    
    # Update status to in_progress if waiting
    if triage.status == 'waiting':
        triage.status = 'in_progress'
        triage.save()
    
    if request.method == 'POST':
        form = TriageForm(request.POST, instance=triage)
        if form.is_valid():
            triage = form.save(commit=False)
            triage.triage_nurse = request.user
            triage.status = 'completed'
            triage.is_completed = True
            triage.completed_at = timezone.now()
            triage.save()
            
            # Check if we should send to doctor immediately
            if request.POST.get('send_to_doctor'):
                triage.send_to_doctor()
                messages.success(request, f'✅ Triage completed and {patient.full_name} sent to doctor!')
            else:
                messages.success(request, f'✅ Triage completed for {patient.full_name}')
            
            return redirect('triage:dashboard')
    else:
        form = TriageForm(instance=triage)
    
    context = {
        'visit': visit,
        'patient': patient,
        'triage': triage,
        'form': form,
    }
    return render(request, 'triage/triage_patient.html', context)


@login_required
def send_to_doctor(request, triage_id):
    """Send patient to doctor"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        messages.error(request, 'Access denied. Triage nurses only.')
        return redirect('core:dashboard')
    
    triage = get_object_or_404(TriageRecord, id=triage_id)
    
    if request.method == 'POST':
        triage.send_to_doctor()
        messages.success(request, f'✅ Patient {triage.patient.full_name} sent to doctor!')
        return redirect('triage:dashboard')
    
    context = {'triage': triage}
    return render(request, 'triage/send_to_doctor.html', context)


@login_required
def nursing_care(request, triage_id):
    """Provide nursing care to patient"""
    if request.user.role not in ['nurse', 'triage', 'admin']:
        messages.error(request, 'Access denied. Nurses only.')
        return redirect('core:dashboard')
    
    triage = get_object_or_404(TriageRecord, id=triage_id, status='nursing_care')
    
    if request.method == 'POST':
        form = NursingCareForm(request.POST, instance=triage)
        if form.is_valid():
            triage = form.save(commit=False)
            triage.nursing_care_completed = True
            triage.nursing_care_completed_at = timezone.now()
            triage.status = 'completed_care'
            triage.save()
            
            # Update visit status - patient goes back to doctor
            triage.visit.status = 'with_doctor'
            triage.visit.save()
            
            messages.success(request, f'✅ Nursing care completed for {triage.patient.full_name}')
            return redirect('triage:dashboard')
    else:
        form = NursingCareForm(instance=triage)
    
    context = {
        'triage': triage,
        'patient': triage.patient,
        'form': form,
    }
    return render(request, 'triage/nursing_care.html', context)


@login_required
def triage_queue(request):
    """View full triage queue"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        messages.error(request, 'Access denied. Triage nurses only.')
        return redirect('core:dashboard')
    
    waiting = PatientVisit.objects.filter(
        status='triage'
    ).order_by('arrival_time')
    
    paginator = Paginator(waiting, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'waiting_patients': page_obj,
    }
    return render(request, 'triage/queue.html', context)


@login_required
def nursing_care_list(request):
    """View patients needing nursing care"""
    if request.user.role not in ['nurse', 'triage', 'admin']:
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
    return render(request, 'triage/nursing_list.html', context)


@login_required
def complete_triage(request, triage_id):
    """Complete triage without sending to doctor"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        messages.error(request, 'Access denied. Triage nurses only.')
        return redirect('core:dashboard')
    
    triage = get_object_or_404(TriageRecord, id=triage_id)
    
    if request.method == 'POST':
        triage.complete_triage()
        messages.success(request, f'Triage completed for {triage.patient.full_name}')
        return redirect('triage:dashboard')
    
    context = {'triage': triage}
    return render(request, 'triage/complete_triage.html', context)


@login_required
def get_stats(request):
    """AJAX endpoint for triage stats"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    stats = {
        'waiting': PatientVisit.objects.filter(status='triage').count(),
        'in_progress': TriageRecord.objects.filter(status='in_progress').count(),
        'nursing_care': TriageRecord.objects.filter(
            status='nursing_care',
            nursing_care_completed=False
        ).count(),
        'completed_today': TriageRecord.objects.filter(
            completed_at__date=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)


@login_required
def receive_from_doctor(request, triage_id):
    """Receive patient from doctor for nursing care"""
    if request.user.role not in ['triage', 'nurse', 'admin']:
        messages.error(request, 'Access denied. Triage nurses only.')
        return redirect('core:dashboard')
    
    triage = get_object_or_404(TriageRecord, id=triage_id)
    
    if request.method == 'POST':
        instructions = request.POST.get('nursing_instructions', '')
        triage.receive_from_doctor(instructions)
        messages.success(request, f'Patient {triage.patient.full_name} received from doctor for nursing care.')
        return redirect('triage:dashboard')
    
    context = {'triage': triage}
    return render(request, 'triage/receive_from_doctor.html', context)