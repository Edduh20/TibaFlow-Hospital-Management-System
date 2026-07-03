from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from patients.models import Patient, PatientVisit
from doctors.models import LabOrder, ImagingOrder
from .models import LabResult, ImagingResult
from .forms import LabResultForm, ImagingResultForm, ClarificationForm, ClarificationResponseForm


@login_required
def lab_dashboard(request):
    """Laboratory dashboard"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    # Get pending lab tests
    pending_lab = LabOrder.objects.filter(
        status__in=['ordered', 'pending']
    ).order_by('created_at')
    
    # Get pending imaging tests
    pending_imaging = ImagingOrder.objects.filter(
        status__in=['ordered', 'pending']
    ).order_by('created_at')
    
    # Get in progress tests
    in_progress_lab = LabOrder.objects.filter(
        status='in_progress'
    ).order_by('-created_at')
    
    in_progress_imaging = ImagingOrder.objects.filter(
        status='in_progress'
    ).order_by('-created_at')
    
    # Get tests needing clarification
    clarification_needed = LabResult.objects.filter(
        status='clarification_needed'
    ).order_by('clarification_requested_at')
    
    clarification_needed_imaging = ImagingResult.objects.filter(
        status='clarification_needed'
    ).order_by('clarification_requested_at')
    
    # Get completed tests today
    completed_lab_today = LabResult.objects.filter(
        completed_at__date=timezone.now().date()
    ).count()
    
    completed_imaging_today = ImagingResult.objects.filter(
        completed_at__date=timezone.now().date()
    ).count()
    
    context = {
        'pending_lab': pending_lab[:10],
        'pending_lab_count': pending_lab.count(),
        'pending_imaging': pending_imaging[:10],
        'pending_imaging_count': pending_imaging.count(),
        'in_progress_lab': in_progress_lab[:10],
        'in_progress_lab_count': in_progress_lab.count(),
        'in_progress_imaging': in_progress_imaging[:10],
        'in_progress_imaging_count': in_progress_imaging.count(),
        'clarification_needed': clarification_needed[:5],
        'clarification_needed_count': clarification_needed.count(),
        'clarification_needed_imaging': clarification_needed_imaging[:5],
        'clarification_needed_imaging_count': clarification_needed_imaging.count(),
        'completed_lab_today': completed_lab_today,
        'completed_imaging_today': completed_imaging_today,
    }
    return render(request, 'laboratory/dashboard.html', context)


@login_required
def perform_lab_test(request, order_id):
    """Perform a lab test"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    lab_order = get_object_or_404(LabOrder, id=order_id)
    patient = lab_order.patient
    
    # Get or create lab result
    lab_result, created = LabResult.objects.get_or_create(
        lab_order=lab_order,
        patient=patient,
        visit=lab_order.medical_record.visit,
        defaults={'status': 'in_progress'}
    )
    
    # Start test if not started
    if lab_result.status == 'pending':
        lab_result.start_test(request.user)
    
    if request.method == 'POST':
        form = LabResultForm(request.POST, request.FILES, instance=lab_result)
        if form.is_valid():
            lab_result = form.save(commit=False)
            lab_result.complete_test(
                results=lab_result.results,
                notes=lab_result.technician_notes
            )
            
            # Send results to doctor - this will unlock the medical record
            medical_record = lab_order.medical_record
            medical_record.receive_lab_results()
            
            messages.success(request, f'Lab test completed for {patient.full_name}')
            return redirect('laboratory:dashboard')
    else:
        form = LabResultForm(instance=lab_result)
    
    context = {
        'lab_order': lab_order,
        'patient': patient,
        'lab_result': lab_result,
        'form': form,
    }
    return render(request, 'laboratory/perform_lab_test.html', context)


@login_required
def perform_imaging_test(request, order_id):
    """Perform an imaging test"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    imaging_order = get_object_or_404(ImagingOrder, id=order_id)
    patient = imaging_order.patient
    
    # Get or create imaging result
    imaging_result, created = ImagingResult.objects.get_or_create(
        imaging_order=imaging_order,
        patient=patient,
        visit=imaging_order.medical_record.visit,
        defaults={'status': 'in_progress'}
    )
    
    # Start test if not started
    if imaging_result.status == 'pending':
        imaging_result.start_test(request.user)
    
    if request.method == 'POST':
        form = ImagingResultForm(request.POST, request.FILES, instance=imaging_result)
        if form.is_valid():
            imaging_result = form.save(commit=False)
            imaging_result.complete_test(
                findings=imaging_result.findings,
                impressions=imaging_result.impressions,
                notes=imaging_result.technician_notes
            )
            
            # Send results to doctor - this will unlock the medical record
            medical_record = imaging_order.medical_record
            medical_record.receive_imaging_results()
            
            messages.success(request, f'Imaging test completed for {patient.full_name}')
            return redirect('laboratory:dashboard')
    else:
        form = ImagingResultForm(instance=imaging_result)
    
    context = {
        'imaging_order': imaging_order,
        'patient': patient,
        'imaging_result': imaging_result,
        'form': form,
    }
    return render(request, 'laboratory/perform_imaging_test.html', context)


@login_required
def request_clarification(request, result_id, result_type='lab'):
    """Request clarification from doctor for lab test"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    if result_type == 'lab':
        result = get_object_or_404(LabResult, id=result_id)
        patient = result.patient
    else:
        result = get_object_or_404(ImagingResult, id=result_id)
        patient = result.patient
    
    if request.method == 'POST':
        form = ClarificationForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            result.request_clarification(message)
            messages.success(request, f'Clarification requested from doctor for {patient.full_name}')
            return redirect('laboratory:dashboard')
    else:
        form = ClarificationForm()
    
    context = {
        'result': result,
        'patient': patient,
        'form': form,
        'result_type': result_type,
    }
    return render(request, 'laboratory/request_clarification.html', context)


@login_required
def respond_to_clarification(request, result_id, result_type='lab'):
    """Respond to clarification from doctor (for lab tech to see response)"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    if result_type == 'lab':
        result = get_object_or_404(LabResult, id=result_id)
    else:
        result = get_object_or_404(ImagingResult, id=result_id)
    
    context = {
        'result': result,
        'result_type': result_type,
    }
    return render(request, 'laboratory/view_clarification_response.html', context)


@login_required
def lab_queue(request):
    """View all pending lab tests"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    pending = LabOrder.objects.filter(
        status__in=['ordered', 'pending']
    ).order_by('created_at')
    
    paginator = Paginator(pending, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_tests': page_obj,
        'test_type': 'Lab Tests',
    }
    return render(request, 'laboratory/queue.html', context)


@login_required
def imaging_queue(request):
    """View all pending imaging tests"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    pending = ImagingOrder.objects.filter(
        status__in=['ordered', 'pending']
    ).order_by('created_at')
    
    paginator = Paginator(pending, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_tests': page_obj,
        'test_type': 'Imaging Tests',
    }
    return render(request, 'laboratory/imaging_queue.html', context)


@login_required
def completed_tests(request):
    """View completed tests"""
    if request.user.role not in ['lab', 'admin']:
        messages.error(request, 'Access denied. Laboratory technicians only.')
        return redirect('core:dashboard')
    
    completed_lab = LabResult.objects.filter(
        status='completed'
    ).order_by('-completed_at')
    
    completed_imaging = ImagingResult.objects.filter(
        status='completed'
    ).order_by('-completed_at')
    
    paginator_lab = Paginator(completed_lab, 10)
    paginator_imaging = Paginator(completed_imaging, 10)
    
    page_lab = request.GET.get('page_lab')
    page_imaging = request.GET.get('page_imaging')
    
    lab_page = paginator_lab.get_page(page_lab)
    imaging_page = paginator_imaging.get_page(page_imaging)
    
    context = {
        'completed_lab': lab_page,
        'completed_imaging': imaging_page,
    }
    return render(request, 'laboratory/completed_tests.html', context)


@login_required
def get_stats(request):
    """AJAX endpoint for lab stats"""
    if request.user.role not in ['lab', 'admin']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    stats = {
        'pending_lab': LabOrder.objects.filter(status__in=['ordered', 'pending']).count(),
        'pending_imaging': ImagingOrder.objects.filter(status__in=['ordered', 'pending']).count(),
        'in_progress': LabOrder.objects.filter(status='in_progress').count() + 
                       ImagingOrder.objects.filter(status='in_progress').count(),
        'clarification_needed': LabResult.objects.filter(status='clarification_needed').count() +
                                ImagingResult.objects.filter(status='clarification_needed').count(),
        'completed_today': LabResult.objects.filter(
            completed_at__date=timezone.now().date()
        ).count() + ImagingResult.objects.filter(
            completed_at__date=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)