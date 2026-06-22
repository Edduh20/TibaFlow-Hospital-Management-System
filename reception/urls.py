from django.urls import path
from . import views

app_name = 'reception'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Add more URLs as needed
]