from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Interview, InterviewReport

def get_all_interviews(request):
    interviews = Interview.objects.all()
    data = [
            {"id": interview.id,
            "candidate_name": interview.candidate.user.first_name,
            "job_title": interview.job.title, }
        for interview in interviews]

    return JsonResponse(data, safe=False)

def get_interview_details(request, interview_id):
    try:
        interview = Interview.objects.select_related('candidate__user', 'job').get(id=interview_id)
    except Interview.DoesNotExist:
        raise Http404("Interview not found")

    data = {
        "final_score": interview.final_score if interview.final_score is not None else "Not scored yet",
        "candidate_name": interview.candidate.user.first_name,
        "candidate_lastname": interview.candidate.user.last_name,
        "job_title": interview.job.title,
    }

    return JsonResponse(data, safe=False)

def get_interview_report(request, interview_id):
    try:
        interview = Interview.objects.get(id=interview_id)
        report = interview.report  
    except Interview.DoesNotExist:
        raise Http404("Interview not found")
    except InterviewReport.DoesNotExist:
        return JsonResponse({"message": "Report not generated yet."}, status=404)

    data = {
        "resume_summary": report.resume_summary,
        "interview_summary": report.interview_summary,
        "recommendation": report.recommendation,
        "reason": report.reason,
        "key_insights": report.key_insights,  # JSON
        "created_at": report.created_at,
    }

    return JsonResponse(data)

