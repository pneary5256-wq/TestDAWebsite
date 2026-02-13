from django.db import models

class Enquiry(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    role = models.CharField(max_length=50)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
