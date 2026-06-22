from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('reception', 'Receptionist'),
        ('triage', 'Triage Nurse'),
        ('doctor', 'Doctor'),
        ('pharmacy', 'Pharmacist'),
        ('lab', 'Laboratory Technician'),
        ('nurse', 'Nurse'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reception')
    phone_number = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    
    def has_permission(self, permission_name):
        if self.role == 'admin':
            return True
        return self.user_permissions.filter(codename=permission_name).exists()
    
    class Meta:
        db_table = 'users'