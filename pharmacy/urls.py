from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]