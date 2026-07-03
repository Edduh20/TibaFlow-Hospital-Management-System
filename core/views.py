from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum


@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    """Return the current CSRF token for pages with stale POST forms."""
    return JsonResponse({'csrfToken': get_token(request)})


def home(request):
    """Landing page / Home page"""
    return render(request, 'home.html')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.role == 'admin':
        return redirect('core:admin_dashboard')
    elif user.role == 'reception':
        return render(request, 'reception/dashboard.html', context)
    elif user.role == 'triage':
        return render(request, 'triage/dashboard.html', context)
    elif user.role == 'doctor':
        from patients.models import PatientVisit, Patient
        from doctors.models import MedicalRecord, Prescription, LabOrder, ImagingOrder
        
        doctor = user
        today = timezone.now().date()
        
        # Get patients waiting from triage
        waiting_patients = PatientVisit.objects.filter(
            status='with_doctor'
        ).order_by('arrival_time')
        
        # Get doctor's assigned patients
        assigned_patients = Patient.objects.filter(
            primary_physician=doctor
        ).order_by('-created_at')
        
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
        
        context.update({
            'doctor': doctor,
            'waiting_patients': waiting_patients[:10],
            'waiting_count': waiting_patients.count(),
            'assigned_patients': assigned_patients[:10],
            'assigned_count': assigned_patients.count(),
            'my_records': my_records,
            'recent_prescriptions': recent_prescriptions,
            'pending_lab_orders': pending_lab_orders,
            'pending_imaging_orders': pending_imaging_orders,
            'returning_patients': returning_patients,
        })
        
        return render(request, 'doctors/dashboard.html', context)
    elif user.role == 'pharmacy':
        return render(request, 'pharmacy/dashboard.html', context)
    elif user.role == 'lab':
        return render(request, 'laboratory/dashboard.html', context)
    elif user.role == 'nurse':
        return render(request, 'nurses/dashboard.html', context)
    
    return render(request, 'dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard with statistics and insights"""
    if request.user.role != 'admin':
        return redirect('core:dashboard')
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    from patients.models import Patient, PatientVisit, Payment
    
    # Total patients
    total_patients = Patient.objects.count()
    patients_yesterday = Patient.objects.filter(created_at__date=yesterday).count()
    patient_growth = round(((total_patients - patients_yesterday) / max(patients_yesterday, 1)) * 100)
    
    # Today's appointments (visits)
    today_appointments = PatientVisit.objects.filter(created_at__date=today).count()
    yesterday_appointments = PatientVisit.objects.filter(created_at__date=yesterday).count()
    appointment_growth = round(((today_appointments - yesterday_appointments) / max(yesterday_appointments, 1)) * 100)
    
    # Admitted patients
    admitted_patients = Patient.objects.filter(is_admitted=True).count()
    admitted_yesterday = Patient.objects.filter(admission_date__date=yesterday).count()
    admitted_growth = round(((admitted_patients - admitted_yesterday) / max(admitted_yesterday, 1)) * 100)
    
    # Total revenue
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_yesterday = Payment.objects.filter(
        payment_date__date=yesterday,
        payment_status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_growth = round(((total_revenue - revenue_yesterday) / max(revenue_yesterday, 1)) * 100)
    
    # Department distribution
    departments = [
        {'name': 'General Medicine', 'percentage': 40, 'color': '#0d6efd'},
        {'name': 'Pediatrics', 'percentage': 20, 'color': '#198754'},
        {'name': 'Surgery', 'percentage': 15, 'color': '#ffc107'},
        {'name': 'Orthopedics', 'percentage': 15, 'color': '#fd7e14'},
        {'name': 'Others', 'percentage': 10, 'color': '#6c757d'},
    ]
    
    # Recent activity
    recent_activities = []
    
    recent_patients = Patient.objects.order_by('-created_at')[:3]
    for patient in recent_patients:
        recent_activities.append({
            'title': f'New patient registered: {patient.full_name}',
            'time': patient.created_at.strftime('%H:%M • %b %d, %Y'),
            'icon': 'fas fa-user-plus',
            'icon_bg': 'rgba(13, 110, 253, 0.1)',
            'icon_color': '#0d6efd',
        })
    
    recent_visits = PatientVisit.objects.order_by('-created_at')[:3]
    for visit in recent_visits:
        recent_activities.append({
            'title': f'{visit.patient.full_name} started a {visit.get_visit_type_display()} visit',
            'time': visit.created_at.strftime('%H:%M • %b %d, %Y'),
            'icon': 'fas fa-calendar-check',
            'icon_bg': 'rgba(25, 135, 84, 0.1)',
            'icon_color': '#198754',
        })
    
    recent_activities = sorted(recent_activities, key=lambda x: x['time'], reverse=True)[:5]
    
    stats = {
        'total_patients': total_patients,
        'patient_growth': patient_growth,
        'today_appointments': today_appointments,
        'appointment_growth': appointment_growth,
        'admitted_patients': admitted_patients,
        'admitted_growth': admitted_growth,
        'total_revenue': round(total_revenue, 2),
        'revenue_growth': revenue_growth,
    }
    
    context = {
        'user': request.user,
        'stats': stats,
        'departments': departments,
        'recent_activities': recent_activities,
        'today': today,
    }
    
    return render(request, 'admin/dashboard.html', context)
