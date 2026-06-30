from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # Dashboard
    path('', views.doctor_dashboard, name='dashboard'),
    path('queue/', views.patient_queue, name='queue'),
    
    # Patient management
    path('patient/<int:visit_id>/', views.view_patient, name='view_patient'),
    path('patient/<int:visit_id>/record/', views.create_medical_record, name='create_record'),
    path('patient/<int:visit_id>/complete/', views.complete_visit, name='complete_visit'),
    path('next-patient/', views.get_next_patient, name='next_patient'),
    
    # Prescriptions
    path('prescription/<int:record_id>/create/', views.create_prescription, name='create_prescription'),
    path('prescription/<int:record_id>/send-pharmacy/', views.send_to_pharmacy, name='send_to_pharmacy'),
    
    # Lab orders
    path('lab/<int:record_id>/order/', views.order_lab_test, name='order_lab'),
    path('lab/<int:record_id>/receive-results/', views.receive_lab_results, name='receive_lab_results'),
    path('lab/<int:record_id>/cancel/', views.cancel_lab_tests, name='cancel_lab'),
    
    # Imaging orders
    path('imaging/<int:record_id>/order/', views.order_imaging, name='order_imaging'),
    path('imaging/<int:record_id>/receive-results/', views.receive_imaging_results, name='receive_imaging_results'),
    path('imaging/<int:record_id>/cancel/', views.cancel_imaging, name='cancel_imaging'),
    
    # Nursing
    path('nurse/<int:record_id>/send/', views.send_to_nurse, name='send_to_nurse'),
    
    # Complete
    path('complete/<int:record_id>/', views.complete_record, name='complete_record'),
    
    # Discharge
    path('discharge/<int:record_id>/', views.discharge_patient, name='discharge'),
]