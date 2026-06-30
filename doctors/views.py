from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from patients.models import Patient, PatientVisit
from triage.models import TriageRecord
from .models import MedicalRecord, Prescription, LabOrder, ImagingOrder
from .forms import (
    MedicalRecordForm, PrescriptionForm, LabOrderForm, 
    ImagingOrderForm, DischargeForm
)


@login_required
def doctor_dashboard(request):
    """Doctor dashboard with queue and statistics"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    doctor = request.user
    today = datetime.now().date()
    
    # Get patients waiting from triage - priority returns first
    waiting_patients = PatientVisit.objects.filter(
        status='with_doctor'
    ).annotate(
        sort_order=Case(
            When(is_priority_return=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('sort_order', 'arrival_time')
    
    # Get patients in lab
    lab_patients = PatientVisit.objects.filter(
        status='lab'
    ).order_by('arrival_time')
    
    # Get doctor's assigned patients
    assigned_patients = Patient.objects.filter(
        primary_physician=doctor
    ).order_by('-created_at')
    
    # Get today's appointments for this doctor
    today_visits = PatientVisit.objects.filter(
        doctor=doctor,
        arrival_time__date=today
    ).order_by('arrival_time')
    
    # Get patient records created by this doctor
    my_records = MedicalRecord.objects.filter(
        doctor=doctor
    ).order_by('-created_at')[:10]
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        doctor=doctor
    ).order_by('-created_at')[:5]
    
    # Get pending lab and imaging orders
    pending_lab_orders = LabOrder.objects.filter(
        doctor=doctor,
        status__in=['ordered', 'pending']
    ).count()
    
    pending_imaging_orders = ImagingOrder.objects.filter(
        doctor=doctor,
        status__in=['ordered', 'pending']
    ).count()
    
    # Get returning patients count
    returning_patients = waiting_patients.filter(is_priority_return=True).count()
    
    context = {
        'doctor': doctor,
        'waiting_patients': waiting_patients[:10],
        'waiting_count': waiting_patients.count(),
        'lab_count': lab_patients.count(),
        'lab_patients': lab_patients[:5],
        'returning_patients': returning_patients,
        'assigned_patients': assigned_patients[:10],
        'assigned_count': assigned_patients.count(),
        'today_visits': today_visits,
        'today_count': today_visits.count(),
        'my_records': my_records,
        'recent_prescriptions': recent_prescriptions,
        'pending_lab_orders': pending_lab_orders,
        'pending_imaging_orders': pending_imaging_orders,
    }
    
    return render(request, 'doctors/dashboard.html', context)


@login_required
def patient_queue(request):
    """View full patient queue with pagination"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    waiting_patients = PatientVisit.objects.filter(
        status='with_doctor'
    ).annotate(
        sort_order=Case(
            When(is_priority_return=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('sort_order', 'arrival_time')
    
    paginator = Paginator(waiting_patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'waiting_patients': page_obj,
    }
    return render(request, 'doctors/queue.html', context)


@login_required
def view_patient(request, visit_id):
    """View patient details and medical record"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    visit = get_object_or_404(PatientVisit, id=visit_id)
    patient = visit.patient
    triage = get_object_or_404(TriageRecord, visit=visit)
    
    # Get or create medical record
    record = MedicalRecord.objects.filter(visit=visit, doctor=request.user).first()
    
    # Mark visit as with doctor if not already
    if visit.status != 'with_doctor':
        visit.status = 'with_doctor'
        visit.doctor_time = datetime.now()
        visit.save()
    
    context = {
        'patient': patient,
        'visit': visit,
        'triage': triage,
        'record': record,
    }
    return render(request, 'doctors/view_patient.html', context)


@login_required
def create_medical_record(request, visit_id):
    """Create or edit a medical record"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    visit = get_object_or_404(PatientVisit, id=visit_id)
    patient = visit.patient
    triage = get_object_or_404(TriageRecord, visit=visit)
    
    # Check if record already exists
    existing_record = MedicalRecord.objects.filter(visit=visit, doctor=request.user).first()
    
    # Check if locked
    if existing_record and existing_record.is_locked:
        messages.error(request, f'This record is locked: {existing_record.lock_reason}')
        return redirect('doctors:view_patient', visit_id=visit.id)
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=existing_record)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.visit = visit
            record.triage = triage
            record.doctor = request.user
            
            # Handle admission if checked
            if form.cleaned_data.get('is_admitted'):
                if not record.admission_date:
                    record.admission_date = timezone.now()
            
            # Handle ML usage
            ml_used = request.POST.get('ml_used', False)
            record.ml_used = ml_used == 'on' or ml_used == 'True'
            
            record.save()
            
            # Update visit status
            visit.status = 'with_doctor'
            visit.save()
            
            messages.success(request, f'Medical record saved for {patient.full_name}!')
            
            # Check if we should order lab/imaging
            if request.POST.get('order_lab'):
                record.order_lab_tests()
                messages.info(request, 'Lab tests ordered. Record is now locked until results come back.')
            elif request.POST.get('order_imaging'):
                record.order_imaging()
                messages.info(request, 'Imaging ordered. Record is now locked until results come back.')
            
            return redirect('doctors:view_patient', visit_id=visit.id)
    else:
        form = MedicalRecordForm(instance=existing_record, initial={
            'patient': patient,
            'symptoms': triage.chief_complaint if triage else '',
            'doctor': request.user,
        })
    
    context = {
        'form': form,
        'patient': patient,
        'visit': visit,
        'triage': triage,
        'existing_record': existing_record,
    }
    return render(request, 'doctors/create_record.html', context)


@login_required
def create_prescription(request, record_id):
    """Create a prescription for a patient"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if record.is_locked:
        messages.error(request, f'Cannot create prescription. Record is locked: {record.lock_reason}')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    patient = record.patient
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.medical_record = record
            prescription.patient = patient
            prescription.doctor = request.user
            prescription.save()
            
            messages.success(request, f'Prescription for {patient.full_name} created successfully!')
            
            # Send to pharmacy if requested
            if request.POST.get('send_to_pharmacy'):
                record.send_to_pharmacy()
                messages.info(request, 'Prescription sent to pharmacy.')
            
            return redirect('doctors:view_patient', visit_id=record.visit.id)
    else:
        form = PrescriptionForm()
    
    context = {
        'form': form,
        'record': record,
        'patient': patient,
    }
    return render(request, 'doctors/create_prescription.html', context)


@login_required
def order_lab_test(request, record_id):
    """Order a lab test"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    patient = record.patient
    
    if record.is_locked:
        messages.error(request, f'Cannot order lab tests. Record is locked: {record.lock_reason}')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    if request.method == 'POST':
        form = LabOrderForm(request.POST)
        if form.is_valid():
            lab_order = form.save(commit=False)
            lab_order.medical_record = record
            lab_order.patient = patient
            lab_order.doctor = request.user
            lab_order.save()
            
            # Lock the record
            record.order_lab_tests()
            
            messages.success(request, f'Lab test ordered for {patient.full_name}! Record is now locked.')
            return redirect('doctors:view_patient', visit_id=record.visit.id)
    else:
        form = LabOrderForm()
    
    context = {
        'form': form,
        'record': record,
        'patient': patient,
    }
    return render(request, 'doctors/order_lab.html', context)


@login_required
def order_imaging(request, record_id):
    """Order an imaging test"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    patient = record.patient
    
    if record.is_locked:
        messages.error(request, f'Cannot order imaging. Record is locked: {record.lock_reason}')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    if request.method == 'POST':
        form = ImagingOrderForm(request.POST)
        if form.is_valid():
            imaging_order = form.save(commit=False)
            imaging_order.medical_record = record
            imaging_order.patient = patient
            imaging_order.doctor = request.user
            imaging_order.save()
            
            record.order_imaging()
            
            messages.success(request, f'Imaging test ordered for {patient.full_name}! Record is now locked.')
            return redirect('doctors:view_patient', visit_id=record.visit.id)
    else:
        form = ImagingOrderForm()
    
    context = {
        'form': form,
        'record': record,
        'patient': patient,
    }
    return render(request, 'doctors/order_imaging.html', context)


@login_required
def receive_lab_results(request, record_id):
    """Receive lab results and unlock the record"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        record.receive_lab_results()
        messages.success(request, f'Lab results received for {record.patient.full_name}. Record unlocked and patient returned to queue.')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    return redirect('doctors:view_patient', visit_id=record.visit.id)


@login_required
def receive_imaging_results(request, record_id):
    """Receive imaging results and unlock the record"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        record.receive_imaging_results()
        messages.success(request, f'Imaging results received for {record.patient.full_name}. Record unlocked and patient returned to queue.')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    return redirect('doctors:view_patient', visit_id=record.visit.id)


@login_required
def send_to_pharmacy(request, record_id):
    """Send prescription to pharmacy"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        record.send_to_pharmacy()
        messages.success(request, f'Prescription sent to pharmacy for {record.patient.full_name}.')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    return redirect('doctors:view_patient', visit_id=record.visit.id)


@login_required
def send_to_nurse(request, record_id):
    """Send patient to nurse for care"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        instructions = request.POST.get('nursing_instructions', '')
        record.send_to_nurse(instructions)
        messages.success(request, f'Patient {record.patient.full_name} sent to nurse for care.')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    context = {
        'record': record,
        'patient': record.patient,
    }
    return render(request, 'doctors/send_to_nurse.html', context)


@login_required
def complete_record(request, record_id):
    """Complete the medical record"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if record.is_locked:
        messages.error(request, f'Cannot complete record. It is locked: {record.lock_reason}')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    if request.method == 'POST':
        # Complete the record
        record.complete_record()
        
        # Ensure the visit is in the queue for completion
        record.visit.status = 'with_doctor'
        record.visit.save()
        
        messages.success(request, f'✅ Medical record for {record.patient.full_name} completed successfully!')
        messages.info(request, 'Click "Complete Visit" to finish and move to the next patient.')
        return redirect('doctors:view_patient', visit_id=record.visit.id)
    
    context = {'record': record}
    return render(request, 'doctors/complete_record.html', context)


@login_required
def complete_visit(request, visit_id):
    """Complete the entire visit and move to next patient"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    visit = get_object_or_404(PatientVisit, id=visit_id)
    
    # Check if there's a medical record
    record = MedicalRecord.objects.filter(visit=visit, doctor=request.user).first()
    
    # Don't allow completion if record is locked (waiting for lab/imaging)
    if record and record.is_locked:
        messages.error(request, f'Cannot complete visit. Record is locked: {record.lock_reason}')
        return redirect('doctors:view_patient', visit_id=visit.id)
    
    # Don't allow completion if record exists but is not completed
    if record and not record.is_completed and record.workflow_status != 'completed':
        messages.error(request, 'Cannot complete visit. Medical record must be completed first.')
        return redirect('doctors:view_patient', visit_id=visit.id)
    
    # If no record exists, redirect to create one
    if not record:
        messages.warning(request, 'Please create a medical record first.')
        return redirect('doctors:create_record', visit_id=visit.id)
    
    if request.method == 'POST':
        # Mark visit as completed
        visit.status = 'completed'
        visit.completed_time = datetime.now()
        visit.is_priority_return = False
        visit.return_from_lab = False
        visit.return_from_imaging = False
        visit.save()
        
        # Mark medical record as completed if not already
        if record and not record.is_completed:
            record.complete_record()
        
        messages.success(request, f'✅ Visit completed for {visit.patient.full_name}!')
        
        # Get the next patient in queue (priority first)
        next_patient = PatientVisit.objects.filter(
            status='with_doctor'
        ).annotate(
            sort_order=Case(
                When(is_priority_return=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by('sort_order', 'arrival_time').first()
        
        if next_patient:
            messages.info(request, f'Next patient: {next_patient.patient.full_name}')
            return redirect('doctors:view_patient', visit_id=next_patient.id)
        else:
            messages.info(request, 'No more patients in queue.')
            return redirect('doctors:dashboard')
    
    return redirect('doctors:view_patient', visit_id=visit.id)


@login_required
def get_next_patient(request):
    """AJAX endpoint to get the next patient in queue"""
    if request.user.role != 'doctor':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get the next patient - priority returns first, then by arrival time
    next_visit = PatientVisit.objects.filter(
        status='with_doctor'
    ).annotate(
        sort_order=Case(
            When(is_priority_return=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('sort_order', 'arrival_time').first()
    
    if next_visit:
        return JsonResponse({
            'visit_id': next_visit.id,
            'patient_name': next_visit.patient.full_name,
            'visit_number': next_visit.visit_number,
            'is_priority': next_visit.is_priority_return,
        })
    else:
        return JsonResponse({'message': 'No patients waiting'})


@login_required
def discharge_patient(request, record_id):
    """Discharge an admitted patient"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        form = DischargeForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.is_admitted = False
            record.discharge_date = timezone.now()
            record.days_of_stay = (record.discharge_date - record.admission_date).days if record.admission_date else 0
            record.save()
            
            patient = record.patient
            patient.is_admitted = False
            patient.discharge_date = timezone.now()
            patient.save()
            
            messages.success(request, f'Patient {patient.full_name} discharged successfully!')
            return redirect('doctors:view_patient', visit_id=record.visit.id)
    else:
        form = DischargeForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
        'patient': record.patient,
        'days_of_stay': record.current_days_of_stay,
    }
    return render(request, 'doctors/discharge.html', context)


@login_required
def cancel_lab_tests(request, record_id):
    """Cancel lab tests and return patient to queue"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        # Cancel the lab orders
        LabOrder.objects.filter(medical_record=record, status__in=['ordered', 'pending']).update(status='cancelled')
        record.cancel_lab_tests()
        messages.success(request, f'Lab tests cancelled. {record.patient.full_name} returned to queue.')
        return redirect('doctors:dashboard')
    
    context = {'record': record}
    return render(request, 'doctors/cancel_lab.html', context)


@login_required
def cancel_imaging(request, record_id):
    """Cancel imaging and return patient to queue"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('core:dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        # Cancel the imaging orders
        ImagingOrder.objects.filter(medical_record=record, status__in=['ordered', 'pending']).update(status='cancelled')
        record.cancel_imaging()
        messages.success(request, f'Imaging cancelled. {record.patient.full_name} returned to queue.')
        return redirect('doctors:dashboard')
    
    context = {'record': record}
    return render(request, 'doctors/cancel_imaging.html', context)