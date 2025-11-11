from django.db import models
from django.conf import settings
from services.models import ServiceType
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Provider(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_profile'
        )
    
    description = models.TextField(blank=True, null=True)
    stars = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )

    cpf = models.CharField(max_length=14, unique=True)
    is_active = models.BooleanField(default=False)
    service_types = models.ManyToManyField(ServiceType, related_name='providers')

    def __str__(self):
        return f"Provider: {self.user.username} - Stars: {self.stars}"


class ProviderApplication(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_applications')
    description = models.TextField(blank=True, null=True)
    cpf = models.CharField(max_length=14)
    service_types = models.ManyToManyField(ServiceType, related_name='applications', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_provider_applications')

    class Meta:
        unique_together = ('applicant', 'cpf')

    def __str__(self):
        return f"ProviderApplication: {self.applicant.username} - {self.status}"