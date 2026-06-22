from django.urls import path
from . import views

app_name = 'nurses'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]