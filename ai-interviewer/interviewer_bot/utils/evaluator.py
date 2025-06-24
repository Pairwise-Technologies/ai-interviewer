from openai import OpenAI
import json

def evaluate_response_action(client: OpenAI, category: str, category_qa: str) -> tuple[str, str | None]:
    """
    Evaluates a Q&A text string for a category and returns a classification:
        - proceed
        - follow_up
        - re_ask
    Optionally provides a follow-up suggestion if applicable.

    Parameters: 
        client: OpenAI
            the bot which is used to evaluate the question and answer
        category: str 
            current category 
        category_qa: str
            the question and answer associated with the category

    Returns:
        action (str): one of 'proceed', 'follow_up', 're_ask'
        followup_suggestion (str or None): A follow-up question or clarification suggestion if needed
    """

    # qa_text = "Q: " + question + "\n"
    # qa_text += "A: " + answer + "\n\n"


    system_prompt = (
        "You're an AI interview evaluator. Analyze the following Q&A and decide if it is appropriate to proceed, "
        "follow up with a clarification, or re-ask the question entirely. "
        "Base your judgment on whether the response is complete, relevant, and addresses the interview question well."
    )

    user_prompt = f"""Category: "{category}"\n\nResponses:\n{category_qa}
    
    Return a JSON object with:
    - "action": one of "proceed", "follow_up", or "re_ask"
    - "followup_suggestion": a short follow-up question (only if action is 'follow_up' or 're_ask') or null otherwise.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "evaluate_action",
                "schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["proceed", "follow_up", "re_ask"],
                            "description": "Classification of whether to move forward with the interview.",
                        },
                        "followup_suggestion": {
                            "type": ["string", "null"],
                            "description": "A follow-up question or clarification prompt if needed.",
                        },
                    },
                    "required": ["action", "followup_suggestion"],
                    "additionalProperties": False,
                },
            },
        },
    )


    bot_response = response.choices[0].message

    if bot_response.content:
        parsed = json.loads(bot_response.content)
        #print("***TESTING: PARSED action: ", parsed["action"])
        return parsed["action"], parsed["followup_suggestion"]
    else:
        return "re_ask", "Unable to evaluate due to an error."
