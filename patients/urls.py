from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Patient List
    path('', views.patient_list, name='list'),
    path('search/', views.patient_list, name='search'),
    
    # Patient CRUD
    path('create/', views.patient_create, name='create'),
    path('<int:patient_id>/', views.patient_detail, name='detail'),
    path('<int:patient_id>/edit/', views.patient_edit, name='edit'),
    path('<int:patient_id>/delete/', views.patient_delete, name='delete'),
    
    # Patient Actions
    path('<int:patient_id>/admit/', views.patient_admit, name='admit'),
    path('<int:patient_id>/discharge/', views.patient_discharge, name='discharge'),
    
    # Export
    path('export/', views.patient_export, name='export'),
    
    # AJAX
    path('api/stats/', views.get_patient_stats, name='stats'),
    path('api/<int:patient_id>/medical-history/', views.patient_medical_history, name='medical_history'),
]