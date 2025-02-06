from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from datetime import timedelta
from django_filters import rest_framework as filters

from django.utils import timezone
class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class JobNameFilter(filters.FilterSet):

 
    name = filters.CharFilter(field_name='title', lookup_expr='contains')

    class Meta:
        model = Job
        fields = ['title']

class JobListView(ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['job_type', 'location', 'salary','currency']
    search_fields = ['title', 'description', 'company']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        print(self.request.query_params)
        # Filter by minimum salary
        min_salary = self.request.query_params.get('min_salary')
        if min_salary:
            queryset = queryset.filter(salary__gte=min_salary)

        # Filter by published time (last n days)
        publish_time = self.request.query_params.get('publish_time')

     
        if publish_time == 'week}':
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
        elif publish_time == '3days}':
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=3))
        elif publish_time == 'month}':
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))
        
        
        
        job_type_param = [job_type.strip() for job_type in self.request.query_params.getlist('job_type')]

        
        if job_type_param:
            queryset = queryset.filter(job_type__in=job_type_param)

        return queryset

    def get(self, request, *args, **kwargs):
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get paginated data
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'count': queryset.count(),  # Include total count of filtered jobs
                'results': serializer.data
            })

        # If pagination is not used, return full data
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),  # Include total count of filtered jobs
            'results': serializer.data
        })

class SavedJobView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Query saved jobs for the authenticated user
        saved_jobs = SavedJob.objects.filter(user=request.user)
        serializer = SavedJobSerializer(saved_jobs, many=True)
        
        data = {
            "count": saved_jobs.count(),
            "jobs": serializer.data
        }
        return Response(data)

    def post(self, request):
        job_id = request.data.get('job_id')
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        if not created:
            return Response({'message': 'Job is already saved'}, status=status.HTTP_200_OK)

        return Response({'message': 'Job saved successfully'}, status=status.HTTP_201_CREATED)



class SavedJobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, job_id):
        try:
            saved_job = SavedJob.objects.get(user=request.user, job_id=job_id)
            saved_job.delete()
            return Response({'message': 'Job removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response({'error': 'Saved job not found'}, status=status.HTTP_404_NOT_FOUND)


class RecentJobView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_jobs = RecentJob.objects.filter(user=request.user)
        serializer = RecentJobSerializer(recent_jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        job_id = request.data.get('job_id')
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        recent_job, created = RecentJob.objects.update_or_create(
            user=request.user, job=job,
            defaults={'viewed_at': timezone.now()}
        )
        return Response({'message': 'Job added to recent jobs'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def job_list(request):
    """View to list all jobs."""
    jobs = Job.objects.all()
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def job_create(request):
    """View to create a new job."""
    serializer = JobSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access': access_token,
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated via token
def get_profile(request):
    try:
        # Get the profile of the currently authenticated user
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated via token
def update_about_me(request):
    try:
        # Get the profile of the currently authenticated user
        profile = Profile.objects.get(user=request.user)

        # Check if 'about_me' field is in the request data
        about_me = request.data.get('about_me')
        if about_me:
            profile.about_me = about_me
            profile.save()

            # Serialize the updated profile data
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "'about_me' field is required."}, status=status.HTTP_400_BAD_REQUEST)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_or_create_work_experience(request):
    try:
        # Fetch the user's profile
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Parse the request data
    experiences = request.data.get('experiences', [])
    delete_ids = request.data.get('delete_ids', [])  # List of IDs to delete

    if not isinstance(experiences, list) or not isinstance(delete_ids, list):
        return Response(
            {"detail": "Invalid request format. Expected 'experiences' to be a list and 'delete_ids' to be a list."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        updated_experiences = []
        created_experiences = []
        
        # Handle updates and creations
        for experience_data in experiences:
            if 'id' in experience_data:
                experience_id = experience_data.pop('id')
                try:
                    experience = WorkExperience.objects.get(id=experience_id, profile=profile)
                except WorkExperience.DoesNotExist:
                    return Response({"detail": f"Work experience with ID {experience_id} not found."}, status=status.HTTP_404_NOT_FOUND)
                
                serializer = WorkExperiencePostSerializer(experience, data=experience_data, partial=True)
                if serializer.is_valid():
                    updated_experiences.append(serializer.save())
                else:
                    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                experience_data['profile'] = profile.id
                serializer = WorkExperiencePostWithOutIDSerializer(data=experience_data)
                if serializer.is_valid():
                    created_experiences.append(serializer.save())
                else:
                    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Handle deletions
        if delete_ids:
            deleted_count, _ = WorkExperience.objects.filter(id__in=delete_ids, profile=profile).delete()

        response_data = {}
        if updated_experiences:
            response_data['updated'] = WorkExperiencePostSerializer(updated_experiences, many=True).data
        if created_experiences:
            response_data['created'] = WorkExperienceSerializer(created_experiences, many=True).data
        if delete_ids:
            response_data['deleted_count'] = deleted_count

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_work_experience(request):
    try:
        # Get the profile of the currently authenticated user
        profile = Profile.objects.get(user=request.user)
        
        # Serialize the work_experiences only
        work_experience_serializer = WorkExperienceSerializer(profile.work_experiences.all(), many=True)
        return Response(work_experience_serializer.data)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_education_list(request):
    try:
        profile = Profile.objects.get(user=request.user)

        educations = EducationSerializer(profile.educations.all(), many=True)
        return Response(educations.data)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated via token
def save_education(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)


    experiences = request.data.get('educations', [])
    delete_ids = request.data.get('delete_ids', [])  # List of IDs to delete

    if not isinstance(experiences, list) or not isinstance(delete_ids, list):
        return Response(
            {"detail": "Invalid request format. Expected 'experiences' to be a list and 'delete_ids' to be a list."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        updated_experiences = []
        created_experiences = []
        for experience_data in experiences:
            
            if 'id' in experience_data:
                experience_id = experience_data.pop('id')
                experience = Education.objects.get(id=experience_id, profile=profile)
                serializer = EducationPostSerializer(experience, data=experience_data, partial=True)
                if serializer.is_valid():
                    updated_experiences.append(serializer.save())
                else:
                    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(experience_data)
                experience_data['profile'] = profile.id
                serializer = EducationPostWithoutIdSerializer(data=experience_data)
                if serializer.is_valid():
                    created_experiences.append(serializer.save())
                else:
                    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        if delete_ids:
            deleted_count, _ = WorkExperience.objects.filter(id__in=delete_ids, profile=profile).delete()

        response_data = {}
        if updated_experiences:
            response_data['updated'] = EducationPostSerializer(updated_experiences, many=True).data
        if created_experiences:
            response_data['created'] = EducationSerializer(created_experiences, many=True).data
        if delete_ids:
            response_data['deleted_count'] = deleted_count
            
        return Response(response_data, status=status.HTTP_200_OK)

    except WorkExperience.DoesNotExist:
        return Response({"detail": f"Work experience with ID {experience_id} not found or does not belong to the user."}, status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        return Response({"detail": "Missing 'id' in experience data (for updates)."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated via token
def save_skills(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SkillsSerializer(data=request.data)
    if serializer.is_valid():
        profile.skills = serializer.validated_data['skills']
        profile.save()
        return Response({"detail": "Skills saved successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAuthenticated])
class ResumeUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def post(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user_id=request.user)  # Get the profile by user ID

            if 'resume' in request.FILES:
                profile.resume = request.FILES['resume']  # Assign the uploaded file to the resume field
                profile.save()

                return Response({"message": "Resume uploaded successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)