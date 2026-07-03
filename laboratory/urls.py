from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    # Dashboard
    path('', views.lab_dashboard, name='dashboard'),
    
    # Lab tests
    path('lab/<int:order_id>/perform/', views.perform_lab_test, name='perform_lab_test'),
    path('lab/queue/', views.lab_queue, name='lab_queue'),
    
    # Imaging tests
    path('imaging/<int:order_id>/perform/', views.perform_imaging_test, name='perform_imaging_test'),
    path('imaging/queue/', views.imaging_queue, name='imaging_queue'),
    
    # Clarification
    path('clarification/lab/<int:result_id>/', views.request_clarification, name='request_clarification'),
    path('clarification/imaging/<int:result_id>/', views.request_clarification, 
         {'result_type': 'imaging'}, name='request_clarification_imaging'),
    path('clarification/response/<int:result_id>/', views.respond_to_clarification, 
         name='clarification_response'),
    path('clarification/response/imaging/<int:result_id>/', views.respond_to_clarification, 
         {'result_type': 'imaging'}, name='clarification_response_imaging'),
    
    # Completed tests
    path('completed/', views.completed_tests, name='completed_tests'),
    
    # AJAX
    path('api/stats/', views.get_stats, name='stats'),
]