# yourapp/urls.py
from django.urls import path
from .views import register, CustomTokenObtainPairView,ResumeUploadView,JobListView
from . import views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('jobs/', views.job_list, name='job-list'),
    path('jobs/create/', views.job_create, name='job-create'),
    path('saved-jobs/', views.SavedJobView.as_view(), name='saved-jobs'),
    path('recent-jobs/', views.RecentJobView.as_view(), name='recent-jobs'),
    path('saved-jobs/<int:job_id>/', views.SavedJobDetailView.as_view(), name='saved-job-detail'),
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/about', views.update_about_me, name='update_about'),
    path('profile/work_experience/', views.update_or_create_work_experience, name='update_or_create_work_experience'),
    path('profile/work_experience/list/', views.get_work_experience, name='get_work_experience'),
    path('profile/education/', views.save_education, name='save_education'),
    path('profile/education/list', views.get_education_list, name='get_education_list'),
    path('profile/skills/', views.save_skills, name='save_skills'),
    path('upload_resume/', ResumeUploadView.as_view(), name='upload_resume'),  # URL pattern for the FBV
    path('jobsf/', JobListView.as_view(), name='job-list'),
]
