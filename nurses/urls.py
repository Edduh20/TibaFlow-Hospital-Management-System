from django.urls import path
from . import views

app_name = 'nurses'

urlpatterns = [
    # Dashboard
    path('', views.nurse_dashboard, name='dashboard'),
    
    # Patient management
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Notes
    path('patient/<int:patient_id>/note/', views.add_nurse_note, name='add_note'),
    
    # Medications
    path('patient/<int:patient_id>/medication/<int:prescription_id>/administer/', 
         views.administer_medication, name='administer_medication'),
    path('medications/pending/', views.pending_medications, name='pending_medications'),
    
    # Observations
    path('patient/<int:patient_id>/observation/', views.add_observation, name='add_observation'),
    
    # Nursing care
    path('nursing-care/', views.nursing_care_patients, name='nursing_care_list'),
    
    # AJAX
    path('api/stats/', views.get_stats, name='stats'),
]