from django.db import models
from django.conf import settings
from services.models import ServiceType
from providers.models import Provider
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ServiceRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    requested_date = models.DateTimeField(auto_now_add=True)

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='made_requests'
    )

    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_requests'
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ServiceRequest: {self.title} by {self.client.username}"

    def save(self, *args, **kwargs):
        try:
            old = ServiceRequest.objects.get(pk=self.pk)
            old_status = old.status
        except ServiceRequest.DoesNotExist:
            old_status = None

        if self.status == self.STATUS_COMPLETED and (old_status != self.STATUS_COMPLETED or not self.completion_date):
            self.completion_date = timezone.now()

        if self.status != self.STATUS_COMPLETED and old_status == self.STATUS_COMPLETED:
            self.completion_date = None

        super().save(*args, **kwargs)


class Rating(models.Model):
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='ratings')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.db.models import Avg
        avg = self.provider.ratings.aggregate(avg_score=Avg('score'))['avg_score']
        if avg is None:
            avg = Decimal('0.00')
        self.provider.stars = avg
        self.provider.save()

    def __str__(self):
        return f"Rating: {self.score} for {self.provider} by {self.reviewer}"