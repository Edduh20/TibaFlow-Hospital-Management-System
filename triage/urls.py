from django.urls import path
from . import views

app_name = 'triage'

urlpatterns = [
    # Dashboard
    path('', views.triage_dashboard, name='dashboard'),
    path('queue/', views.triage_queue, name='queue'),
    
    # Triage
    path('patient/<int:visit_id>/', views.triage_patient, name='triage_patient'),
    path('complete/<int:triage_id>/', views.complete_triage, name='complete_triage'),
    path('send-doctor/<int:triage_id>/', views.send_to_doctor, name='send_to_doctor'),
    
    # Nursing Care
    path('nursing/<int:triage_id>/', views.nursing_care, name='nursing_care'),
    path('nursing/list/', views.nursing_care_list, name='nursing_list'),
    
    # AJAX
    path('api/stats/', views.get_stats, name='stats'),
]