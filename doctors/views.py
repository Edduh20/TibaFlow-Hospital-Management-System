from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accounts.decorators import app_role_required

@login_required
@app_role_required('doctors')
def dashboard(request):
    return render(request, 'doctors/dashboard.html', {'user': request.user})