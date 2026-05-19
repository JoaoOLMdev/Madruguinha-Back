from django.db import models

class Location(models.Model):
    display_name = models.CharField(max_length=255)
    lat = models.CharField(max_length=50)
    lon = models.CharField(max_length=50)
    osm_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    osm_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name
