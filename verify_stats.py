import os
import django
from rest_framework.test import APIRequestFactory, force_authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.contrib.auth.models import User
from backend.api.views import DashboardStatsView

def verify():
    u = User.objects.get(username='comercial')
    print(f"Testing access for user: {u.username} (Role: {u.ejecutivo.rol.nombre})")
    
    factory = APIRequestFactory()
    view = DashboardStatsView.as_view()
    
    request = factory.get('/api/dashboard-stats/')
    force_authenticate(request, user=u)
    response = view(request)
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    if response.status_code == 403:
        print("SUCCESS: Access BLOCKED as expected.")
    else:
        print("FAILURE: Access allowed or unexpected status.")

if __name__ == "__main__":
    verify()
