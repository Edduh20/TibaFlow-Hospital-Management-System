from django.urls import path
from . import views

app_name = 'reception'

urlpatterns = [
    # Dashboard
    path('', views.reception_dashboard, name='dashboard'),
    path('queue/', views.patient_queue, name='queue'),
    
    # Patient management
    path('patient/register/', views.register_patient, name='register_patient'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patient/search/', views.patient_search, name='patient_search'),
    
    # Triage
    path('triage/<int:visit_id>/', views.send_to_triage, name='send_to_triage'),
    
    # Insurance
    path('insurance/<int:visit_id>/', views.verify_insurance, name='verify_insurance'),
    
    # AJAX
    path('api/stats/', views.get_quick_stats, name='quick_stats'),
    
]