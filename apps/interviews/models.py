from django.db import models

# Create your models here.

from django.db import models
from jobs.models import Job 
from profiles.models import TalentProfile 
from core.models import Timestampable
import uuid 

class InterviewStatusChoices(models.TextChoices):
    SCHEDULED = "scheduled"
    AWAITING_FEEDBACK = "awaiting_feedback"
    COMPLETE = "complete"

class Interview(Timestampable):
    start = models.DateTimeField(
            null=True, blank=True, help_text="Start time of the interview"
        )
    end = models.DateTimeField(
            null=True, blank=True, help_text="End time of the interview"
        )

    candidate = models.ForeignKey(
            TalentProfile,
            related_name="job_applications",
            on_delete=models.CASCADE,
            null=True,
        )

    job = models.ForeignKey(
            Job,
            related_name="job_applications",
            on_delete=models.CASCADE,
            null=True
        )

    status = models.CharField(
            max_length=50,
            choices=InterviewStatusChoices.choices,
            default=InterviewStatusChoices.SCHEDULED,
        )

    # can be moved to interviewreport
    final_score = models.FloatField(null=True, blank=True, help_text="Final weighted score for the interview")


class InterviewReport(models.Model):
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE,related_name="report")

    resume_summary = models.TextField()  #resume summary
    interview_summary = models.TextField() #interview summary 

    recommendation = models.CharField(max_length=20, 
        choices=[("recommended", "Recommended"),("not recommended", "Not Recommended")]) # whether or not candidate recommended

    reason = models.TextField()  # reason for recommendation

    key_insights = models.JSONField( default=list, help_text="List of 5 key insights, each with a 'text' and 'label' (good/bad)" ) # 5 interview key points

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for Interview {self.interview.id}"
