from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Prediction(models.Model):
    id = models.BigAutoField(primary_key=True)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now, blank=True)
    image_file = models.ImageField(upload_to="images/", null=True, blank=True)
    # Fields for storing prediction classes and probabilities
    class_1 = models.CharField(max_length=255, null=True, blank=True)
    prob_1 = models.FloatField(null=True, blank=True)
    class_2 = models.CharField(max_length=255, null=True, blank=True)
    prob_2 = models.FloatField(null=True, blank=True)
    class_3 = models.CharField(max_length=255, null=True, blank=True)
    prob_3 = models.FloatField(null=True, blank=True)
    class_4 = models.CharField(max_length=255, null=True, blank=True)
    prob_4 = models.FloatField(null=True, blank=True)

    def __str__(self):
        submitted_by = self.submitted_by.username if self.submitted_by else "Anonymous"
        return f"Prediction by {submitted_by} on {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
