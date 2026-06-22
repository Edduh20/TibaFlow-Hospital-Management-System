from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
    }
    
    # Redirect to role-specific dashboard
    if user.role == 'admin':
        return render(request, 'admin/dashboard.html', context)
    elif user.role == 'reception':
        return render(request, 'reception/dashboard.html', context)
    elif user.role == 'triage':
        return render(request, 'triage/dashboard.html', context)
    elif user.role == 'doctor':
        return render(request, 'doctors/dashboard.html', context)
    elif user.role == 'pharmacy':
        return render(request, 'pharmacy/dashboard.html', context)
    elif user.role == 'lab':
        return render(request, 'laboratory/dashboard.html', context)
    elif user.role == 'nurse':
        return render(request, 'nurses/dashboard.html', context)
    
    return render(request, 'dashboard.html', context)