from django.db import models
from django.contrib.auth.models import User
from datetime import date
from dateutil.relativedelta import relativedelta  # To calculate the difference in years and months
from dateutil import relativedelta
from datetime import datetime

class Job(models.Model):
    JOB_TYPES = (
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
        ('office', 'Office'),
        ('full-time', 'Full-Time')
    )
    CURRENCY = (
        ('Теңге','Tenge'),
        ('Доллар','Dollar'),
        ('Евро','Euro')
    )

    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=10, choices=JOB_TYPES)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    jdata = models.JSONField(null=True, blank=True)  # Use JSONField instead of ArrayField
    logo = models.ImageField(upload_to='job_logos/', null=True, blank=True)  # Field for logo image
    currency = models.CharField(max_length=10, choices=CURRENCY)
    def __str__(self):
        return self.title


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class RecentJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recent_jobs')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='viewed_by_users')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']  # Show most recent jobs first

    def __str__(self):
        return f"{self.user.username} viewed {self.job.title}"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(null=True, blank=True)
    skills = models.JSONField(null=True, blank=True)  # Store as JSON array of skills
    avatar = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)  # New resume field

    
    def __str__(self):
        return self.user.username

    def get_full_name(self):
        return self.user.get_full_name()  # This will give the user's full name from the User model

    @property
    def profile_picture_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experiences')
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # End date can be null for current jobs
    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company}"

    def get_duration(self):
        start = self.start_date
        end = self.end_date or datetime.now().date()  # Use current date if end_date is null

        # Format the dates as "Month Year"
        start_str = start.strftime("%B %Y")
        end_str = end.strftime("%B %Y") if self.end_date else "Current"

        # Calculate the difference in years and months
        delta = relativedelta.relativedelta(end, start)
        duration_str = f"{delta.years} year{'s' if delta.years != 1 else ''}, {delta.months} month{'s' if delta.months != 1 else ''}"

        return f"{start_str} - {end_str} ({duration_str})"


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    level_of_education = models.CharField(max_length=100)  # e.g., Bachelor's, Master's
    university_name = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.level_of_education} in {self.field_of_study} from {self.university_name}"

    def get_duration(self):
        start = self.start_date
        end = self.end_date or datetime.now().date()  # Use current date if end_date is null

        # Format the dates as "Month Year"
        start_str = start.strftime("%B %Y")
        end_str = end.strftime("%B %Y") if self.end_date else "Current"

        # Calculate the difference in years and months
        delta = relativedelta.relativedelta(end, start)
        duration_str = f"{delta.years} year{'s' if delta.years != 1 else ''}, {delta.months} month{'s' if delta.months != 1 else ''}"

        return f"{start_str} - {end_str} ({duration_str})"