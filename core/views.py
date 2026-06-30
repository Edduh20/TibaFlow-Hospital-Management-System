from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta

# Import the models you need
from patients.models import Patient, PatientVisit
from triage.models import TriageRecord
from doctors.models import MedicalRecord, Prescription, LabOrder, ImagingOrder


def home(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    # Redirect to role-specific dashboard
    if user.role == 'admin':
        # Admin dashboard logic
        return render(request, 'admin/dashboard.html', context)
    
    elif user.role == 'reception':
        # Reception dashboard logic
        return render(request, 'reception/dashboard.html', context)
    
    elif user.role == 'triage':
        # Triage dashboard logic
        return render(request, 'triage/dashboard.html', context)
    
    elif user.role == 'doctor':
        # Doctor dashboard logic
        doctor = user
        today = datetime.now().date()
        
        # Get patients waiting from triage
        waiting_patients = PatientVisit.objects.filter(
            status='with_doctor'
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
        
        # Get pending lab and imaging orders
        pending_lab_orders = LabOrder.objects.filter(
            doctor=doctor,
            status__in=['ordered', 'pending']
        ).count()
        
        pending_imaging_orders = ImagingOrder.objects.filter(
            doctor=doctor,
            status__in=['ordered', 'pending']
        ).count()
        
        context.update({
            'doctor': doctor,
            'waiting_patients': waiting_patients[:10],
            'waiting_count': waiting_patients.count(),
            'assigned_patients': assigned_patients[:10],
            'assigned_count': assigned_patients.count(),
            'today_visits': today_visits,
            'today_count': today_visits.count(),
            'my_records': my_records,
            'pending_lab_orders': pending_lab_orders,
            'pending_imaging_orders': pending_imaging_orders,
        })
        
        return render(request, 'doctors/dashboard.html', context)
    
    elif user.role == 'pharmacy':
        return render(request, 'pharmacy/dashboard.html', context)
    
    elif user.role == 'lab':
        return render(request, 'laboratory/dashboard.html', context)
    
    elif user.role == 'nurse':
        return render(request, 'nurses/dashboard.html', context)
    
    # Fallback
    return render(request, 'dashboard.html', context)