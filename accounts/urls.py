from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Login handled by modal - POST only
    path('login/', views.login_modal, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]