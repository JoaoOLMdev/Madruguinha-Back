from django.db import models
from django.conf import settings
from services.models import ServiceType

class ServiceRequest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    adress = models.CharField(max_length=255)
    requested_date = models.DateTimeField(auto_now_add=True)

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='made_requests'
    )

    ServiceType = models.ForeignKey(
        ServiceType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_requests'
    )

    def __str__(self):
        return f"ServiceRequest: {self.title} by {self.client.username}"