from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Medicine(models.Model):
    CATEGORY_CHOICES = (
        ('medicine', 'Medicine'),
        ('supply', 'Medical Supply'),
        ('equipment', 'Equipment'),
    )
    UNIT_CHOICES = (
        ('tablets', 'Tablets'),
        ('capsules', 'Capsules'),
        ('ml', 'ml'),
        ('bottles', 'Bottles'),
        ('vials', 'Vials'),
        ('units', 'Units'),
    )

    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='medicine')
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tablets')
    reorder_level = models.PositiveIntegerField(default=10)
    storage_location = models.CharField(max_length=100, blank=True)
    supplier = models.CharField(max_length=150, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    def is_expiring_soon(self, within_days=30):
        if not self.expiry_date:
            return False
        return self.expiry_date <= timezone.localdate() + timedelta(days=within_days)


class Prescription(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('dispensed', 'Dispensed'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    PRIORITY_CHOICES = (
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    )

    patient_name = models.CharField(max_length=200)
    patient_age = models.PositiveSmallIntegerField(null=True, blank=True)
    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions_written',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    notes = models.TextField(blank=True)
    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions_dispensed',
    )
    dispensed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} — {self.get_status_display()}"

    @property
    def is_pending(self):
        return self.status == 'pending'


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items',
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescription_items',
    )
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.medicine_name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if self.medicine and not self.medicine_name:
            self.medicine_name = self.medicine.name
        super().save(*args, **kwargs)
