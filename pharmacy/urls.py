from django.urls import path

from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/add/', views.stock_add, name='stock_add'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
]
