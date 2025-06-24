from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from django.contrib import admin
from django.urls import path, include
from .views import ReactAppView
from transcripts import views as transcript_views
from interviews import views as interview_views

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('', ReactAppView.as_view(), name='home'),
]

api_docs = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/documentation/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
urlpatterns += api_docs

urlpatterns += [
    path('api/interviews/', interview_views.get_all_interviews, name='get_all_interviews'),
    path('api/transcripts/', transcript_views.get_all_transcripts, name='get_all_transcripts'),
    path('api/scores/<int:interview_id>/', transcript_views.get_interview_scores, name='get_interview_scores'),
    path('api/interview/<int:interview_id>/details/', interview_views.get_interview_details, name='get_interview_details'),
    path("api/interviews/<int:interview_id>/report/", interview_views.get_interview_report, name= 'get_interview_report'),
]

