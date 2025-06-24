import openai
from openai import OpenAI
import json
from transcripts.models import Transcript, InterviewScore, CategoryChoices
from interviews.models import Interview, InterviewReport

def score_interview(interview: Interview, client:OpenAI) -> None:
    """
    Evaluates the candidate's performance in each interview category and stores the score and reasoning.

    For each distinct category present in the Transcript entries of a given interview, this function:
    - Collects all related Q&A pairs.
    - Uses the LLM to evaluate the responses and return a score and explanation.
    - store the score and explanation in the InterviewScore table.

    Parameters:
        interview (Interview): The interview instance to be scored.
        client (OpenAI): An OpenAI API client used to generate scores for the Q&A pairs.

    Returns:
        None
    """
    # get available categories for specific interview obj 
    categories = (Transcript.objects.filter(interview=interview).exclude(category__isnull=True).values_list('category', flat=True).distinct())

    for category in categories:
        print("Testing: scoring category ", category, ".....")

        # get all q/a pair for this categorys
        qa_pairs = Transcript.objects.filter(interview=interview, category=category)

        # append all pairs for this category
        qa_str = ""
        for pair in qa_pairs:
            qa_str += "Q: " + pair.question + "\n"
            qa_str += "A: " + pair.answer + "\n\n"

        # get score from llm output
        score, reason = get_score(client, category, qa_str)

        # store in db
        InterviewScore.objects.update_or_create(interview=interview, category=category,
                                                 defaults={"score": score,"reason": reason})


    # final score based on non-location categories 
    scores = InterviewScore.objects.filter(interview=interview).exclude(category="location").values_list('score', flat=True)

    if scores:
        final_score = sum(scores) / len(scores)  #AVG 
        final_score = round(final_score, 2)
        # should be stored in interviewReport instead
        interview.final_score = final_score
        interview.save()

    print("Testing: Final Score: ", final_score)



def get_score(client:OpenAI , category: str , qa_text: str)  -> tuple[float | None, str]:
    """
    Sends a formatted set of interview Q&A responses to the OpenAI API to receive a performance score and justification.
    It uses OpenAI's function calling (via JSON schema) to enforce a structured response containing:
        - a numeric score between 1 and 10 (can be float)
        - a short explanation ("reason") for the assigned score.

    Parameters:
        client (OpenAI): The OpenAI API client instance for generating the score.
        category (str): The name of the interview category being evaluated.
        qa_text (str):  string containing all q/a pairs for this category.

    Returns:
            score (float or None): The score assigned by the LLM (1 to 10), or None if generation fails.
            reason (str): The LLM-generated justification for the score, or a fallback error message.
    """

    system_prompt = (
        "You're an AI interviewer assistant helping to evaluate candidate responses. "
        "Your job is to analyze interview answers in a specific category and return a score from 1 to 10, along with a short and brief explanation.")

    user_prompt = f""" Evaluate the following responses in the category: "{category}"
                        Respond with only a JSON object that includes:
                             - "score": a number between 1 and 10 (float allowed)
                             - "reason": a very short explanation for the score
                            \nResponses:{qa_text}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "score_interview",
                "schema": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number",
                            "description": "Score from 1 to 10 evaluating thecandidate's responses in the given category",
                        },
                        "reason": {"type": "string", "description": "reason"},
                    },
                    "required": ["score", "reason"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    )

    bot_response = response.choices[0].message

    if bot_response.content:
        parsed = json.loads(bot_response.content)
        score = parsed["score"]
        reason = parsed["reason"]

    else:
       score = None
       reason =  "Scoring failed due to an error"

    return score, reason

