from django.http import JsonResponse
from transcripts.models import Transcript, InterviewScore
from interviews.models import Interview
from django.shortcuts import get_object_or_404, render


# Get all transcripts for all interview sessions
def get_all_transcripts(request):
    interview_id = request.GET.get('interview_id')
    transcripts = Transcript.objects.all()

    if interview_id:
        transcripts = transcripts.filter(interview_id=interview_id)
        
    transcript_data = [
        {
            "question": transcript.question,
            "answer": transcript.answer,
            "category": transcript.category,
            "interview": {
                "candidate": transcript.interview.candidate.user.first_name,
                "job_title": transcript.interview.job.title,
            }
        }
        for transcript in transcripts
    ]
    return JsonResponse(transcript_data, safe=False)

# Get interview scores for a particular interview id
def get_interview_scores(request, interview_id):
    interview_scores = InterviewScore.objects.filter(interview_id=interview_id)
    score_data = [
        {
            "category": score.category,
            "score": score.score,
            "reason": score.reason,
        }
        for score in interview_scores
    ]
    return JsonResponse(score_data, safe=False)
