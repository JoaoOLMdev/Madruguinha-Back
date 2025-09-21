from django.db import models
from django.conf import settings
from services.models import ServiceType
from django.core.validators import MinValueValidator, MaxValueValidator

class Provider(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_profile'
        )
    
    description = models.TextField(blank=True, null=True)
    stars = models.DecimalField(
        max_digits=2,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )

    is_active = models.BooleanField(default=False)

    servide_types = models.ManyToManyField(ServiceType, related_name='providers')

    def __str__(self):
        return f"Provider: {self.user.username} - Stars: {self.stars}"