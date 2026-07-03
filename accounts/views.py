from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import UserRegistrationForm, UserProfileForm


def login_modal(request):
    """Handle login from modal"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return redirect('/')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            # Redirect to dashboard based on role
            if user.role == 'admin':
                return redirect('core:admin_dashboard')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('/')
    
    return redirect('/')


def logout(request):
    """Logout user"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """User profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})