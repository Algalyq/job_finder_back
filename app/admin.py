from django.contrib import admin
from .models import Job,SavedJob,RecentJob,Profile,Education,WorkExperience

admin.site.register(Job)
admin.site.register(SavedJob)
admin.site.register(RecentJob)
admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(WorkExperience)
