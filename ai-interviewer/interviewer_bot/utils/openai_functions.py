#  currently the interview ending is deterministic, ends when no categories left.
# this can be removed later or made more specific for other stopping criteria.
def end_interview() -> dict:
    """
    Tools used to end interview which is send to the openai bot

    Parameters:
        None
    Returns: 
       dict
            formatted dictionary telling openai what to do 
    """
    return {
        "type": "function",
        "function":
        {
            "name": "end_interview",
            "description": "Ends the interview and returns a summary of the interview and how strong the candidate is.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string",}
                },
                "required": [
                    "summary"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }


def stop_interview_relocation() -> dict:
    """
    Tools used to end the interview if the location of the candidate is not desirable and unable or unwilling to relocate

    Parameters:
        None
    Returns: 
        dict
            formatted dictionary to tell openai what to do
    """
    return {
        "type": "function",
        "function":
        {
            "name": "stop_interview_relocation",
            "description": "Ends the interview if candidate not willing to relocate and returns a summary of the interview and how strong the candidate is.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string",}
                },
                "required": [
                    "summary"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }



def ask_relocation_confirmation() -> dict:
    """
    Tools used to confirm if the candidate is unwilling to relocate which is send to the openai bot

    Parameters:
        None
    Returns: 
        dict
            formatted dictionary telling openai what to do
    """
    return {
        "type": "function",
        "function":
        {
            "name": "ask_relocation_confirmation",
            "description": "if the candidate is not willing to relocate, ask if theyre sure, tell them this means they're not eligible for the position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string",}
                },
                "required": [
                    "question"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
