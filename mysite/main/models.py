from django.db import models
from django.utils.text import slugify

class Enquiry(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    role = models.CharField(max_length=50)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"


class School(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    ATTENDANCE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
    ]
    LOCATION_CHOICES = [
        ('headingley', 'Headingley Campus'),
        ('city', 'City Campus'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='courses')
    image_url = models.URLField(blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    # New fields
    attendance = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='full_time')
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 3 years, 18 months")
    location = models.CharField(max_length=200, blank=True, choices=LOCATION_CHOICES)
    cost = models.CharField(max_length=200, blank=True, help_text="e.g., £9,250 per year")
    entry_requirements = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            # Ensure slug uniqueness by appending a counter when needed.
            counter = 1
            while Course.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        if self.cost:
            normalized_cost = self.cost.strip()
            if normalized_cost and not normalized_cost.startswith("£"):
                self.cost = f"£{normalized_cost}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Module(models.Model):
    LEVEL_CHOICES = [
        ('4', 'Level 4'),
        ('5', 'Level 5'),
        ('6', 'Level 6'),
        ('7', 'Level 7'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES, default='4')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ['level', 'order', 'title']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
