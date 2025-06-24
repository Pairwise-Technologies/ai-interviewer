import json
import time
import uuid
from transcripts.models import Transcript
from interviews.models import Interview 

def write_to_transcript(id: int, user: str, messages: list) -> None:
    '''
    Creates a dictionary, converts it to a json object and writes to a json file
    
    Parameters:
        id : Int 
            Conversation id to link a screening interview transcript to a user
        user : User
            Links the users first name to the transcript 
        messages : list
            Transcript of the message history and who said what during the interview

    Returns: 
        None    
    '''
    transcript = { "conversation_id": id, "interviewee": user, "messages": messages}
    json_obj = json.dumps(transcript, indent=4)
    with open("transcript.json", "w") as file:
        file.write(json_obj)


def write_transcript_to_db(interview: Interview, messages: list)-> None:
    """
    Stores assistant - user messages as transcript entries linked to an interview.

    Pairs assistant questions with user answers. Handles unmatched messages (extra assistant or user )
    and assigns a shared session_id for all entries in a session.

    Parameters:
        interview: Interview
            The interview object to link transcripts to.
        messages: list
            List of dicts with "role" ("assistant" or "user") and "content" (str).

    Returns:
        None
    """
    session_id = uuid.uuid4()
    i = 0
    while i < len(messages):

        # handle paired Q/A
        if i + 1 < len(messages):
            bot_msg = messages[i]
            user_msg = messages[i + 1]
            if bot_msg["role"] == "assistant" and user_msg["role"] == "user":
                category = bot_msg.get("category", None)
                Transcript.objects.create(session_id=session_id, interview=interview,
                                         question=bot_msg["content"], answer=user_msg["content"],
                                         category=category)
                i += 2
                continue

        # handle unpaired Q or A
        msg = messages[i]
        
        #unpaired Q
        if msg["role"] == "assistant":
            category = msg.get("category", None)
            Transcript.objects.create(session_id=session_id  , interview=interview,
                                      question=msg["content"], answer="",
                                      category=category )

        #unpaired A
        elif msg["role"] == "user":
            Transcript.objects.create(session_id=session_id,  interview=interview,
                                      question=""          ,  answer=msg["content"])
        i += 1


