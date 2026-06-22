from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('me/', views.get_current_user, name='me'),
    path('users/', views.get_users, name='users'),
]