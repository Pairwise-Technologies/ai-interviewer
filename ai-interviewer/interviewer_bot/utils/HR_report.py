import openai
from openai import OpenAI
import json
from transcripts.models import Transcript, InterviewScore, CategoryChoices
from interviews.models import Interview , InterviewReport

def generate_report_components(interview: Interview, client:OpenAI) -> None:
    """
    Creates a report based on how the interview went and generates a summary report giving a recommendation.
    
    Parameters: 
        interview : Interview
            the total interview structure with a completed interview
        client : OpenAI
            the bot used to score the candidate
    Returns: 
        None
    """
    candidate = interview.candidate
    job = interview.job

    candidate_resume = candidate.resume.clean_text
    job_description = job.description

    transcripts = Transcript.objects.filter(interview=interview,category__isnull=False).order_by("created_at")

    interview_transcript = ""
    for t in transcripts:
        interview_transcript += f"Q ({t.category}): {t.question}\nA: {t.answer}\n\n"

    interview_transcript = interview_transcript.strip()


    resume_summary, interview_summary, recommendation, reason, key_insights = get_report_components(candidate_resume, job_description, interview_transcript, client)

    print(f"📄 Resume Summary:\n{resume_summary}\n")
    print(f"🗣️ Interview Summary:\n{interview_summary}\n")
    print(f"✅ Recommendation:\n{recommendation}\n")
    print(f"💬 Reason:\n{reason}\n")
    print(f"\nInsights: ")
    for i, insight in enumerate(key_insights, 1):
          print(f"{i}. [{insight['label'].upper()}] {insight['text']}")


    InterviewReport.objects.update_or_create(interview=interview, 
    defaults={
        "resume_summary": resume_summary,
        "interview_summary": interview_summary,
        "recommendation": recommendation,
        "reason": reason,
        "key_insights": key_insights
    })


def get_report_components(resume: str, job_description: str, interview_transcript: str, client: openai.OpenAI) -> dict:
    """
    Utilizes prompts to generate the required information based on the interview candidate
    
    Parameters: 
        resume : str
            Candidates resume 
        job_description : str
            Job the candidate got the interview for 
        interview_transcript : str
            The entire transcript of the interview
        client : opensi.OpenAI
            The bot used to score the candidate
    Returns:
        dict[str]
            returns a dictionary of the report components
    """
    system_prompt = (
        "You are an interview analysis assistant. "
        "Given a resume, job description, and interview transcript, "
        "summarize each and decide whether the candidate is recommended or not for the job."
    )

    user_prompt = f"""Resume:{resume} \n\n
                    Job Description:{job_description} \n\n
                    Interview Transcript:{interview_transcript}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        response_format = {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "interview_report",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "resume_summary": {        # 1
                                            "type": "string",
                                            "description": "Short summary of the candidate's resume"
                                        },
                                        "interview_summary": {     # 2
                                            "type": "string",
                                            "description": "Short summary of the candidate's interview performance"
                                        },
                                        "recommendation": {        # 3
                                            "type": "string",
                                            "enum": ["recommended", "not recommended"],
                                            "description": "Whether the candidate is recommended for the job"
                                        },
                                        "reason": {                # 4
                                            "type": "string",
                                            "description": "Short justification for the recommendation"
                                        },
                                        "key_insights": {          # 5
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "text": {
                                                        "type": "string",
                                                        "description": "A Key insight about the candidate"
                                                    },
                                                    "label": {
                                                        "type": "string",
                                                        "enum": ["good", "bad"],
                                                        "description": "Whether this key insight reflects positively or negatively"
                                                    }
                                                },
                                                "required": ["text", "label"],
                                                "additionalProperties": False
                                            },
                                            "description": "Exactly 5 key insights (good or bad) about the candidate"
                                        }
                                    },
                                    "required": ["resume_summary", "interview_summary", "recommendation", "reason", "key_insights"],
                                    "additionalProperties": False
                                },
                                "strict": True
                            }
}

    )

    bot_response = response.choices[0].message

    if bot_response.content:
        parsed = json.loads(bot_response.content)
        resume_summary = parsed["resume_summary"]
        interview_summary = parsed["interview_summary"]
        recommendation = parsed["recommendation"]
        reason = parsed["reason"]
        key_insights = parsed["key_insights"] 
    else:
        resume_summary = None
        interview_summary = None
        recommendation = None
        reason = None
        key_insights = [] 

    return resume_summary, interview_summary, recommendation, reason, key_insights


