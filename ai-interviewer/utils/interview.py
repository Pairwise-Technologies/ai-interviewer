from .openai_functions import end_interview
import time
import json
from .transcript import write_to_transcript
from .bot import get_bot_response
from .inputs import get_user_input,update_history
from openai import OpenAI
import django
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from profiles.models import TalentProfile
from jobs.models import Job
from locations.models import Location
from .distances import calculate_distance

def conduct_interview(talent: TalentProfile, job: Job,  transcript_messages:list, conversation_history:list, client:OpenAI) -> None:
        '''
        Main structured function for conducting the screening interview

        Inputs: 
            talent: TalentProfile
                The users talent profile 
            job: Job
                Job model which includes information about the specific job
            transcript_messages : list
                The transcript messages meant for the bot and the user
            conversation_history : list
                The conversation history the bot will be using
            client : OpenAI
                The way to API call the bot
        
        Returns:
            None
        '''
        start_time = time.time()
        max_time = 15 * 60  # max time in seconds 
        warning_flag = False
        relocation_flag = False

        job_locations = job.locations.all()  # get all job locations
        talent_locations = talent.locations.all() # get all talent location
        curr_location = talent_locations[0].display_name if talent_locations else "Unknown" # get curr location in case of location update

        distances = calculate_distance(job_locations, talent_locations)
        min_dist = min(distances, key=lambda x: x[2])[2] #sort by dist, get min

        bot_reply = "" 

        while True:
            if  warning_flag == False and time.time() - start_time >= max_time - 60:
                print("Warning: The interview will end in 1 minute.")
                warning_flag = True

            if time.time() - start_time >= max_time:
                print("Time is up! Ending the interview now.")
                break
            
            print("You: ", end='', flush=True)
            user_input = get_user_input()
            if user_input.lower() == "exit": # remove later
                write_to_transcript(talent.user.id, talent.user.first_name, messages=transcript_messages)
                print("Goodbye!")
                break

            if bot_reply and ("currently located" in bot_reply.lower().strip() or "current location" in bot_reply.lower().strip()):
                updated_location, updated_dist = process_location_update(user_input, job_locations)

                if updated_location != "Invalid": 
                    curr_location = updated_location
                    min_dist = updated_dist
                    print(f"updated current location to {curr_location}")
        

            if bot_reply and ("open to relocating" in bot_reply.lower().strip() or "willing to commute" in bot_reply.lower().strip()) and min_dist > 50:
                    if user_input.lower().strip() in ["no", "i can't", "not willing to relocate", "nope", "not sure"]:
                        reconsideration_msg = "Are you sure? This may mean you are not eligible for this position."
                        print("Interviewer:", reconsideration_msg)
                        update_history("assistant", conversation_history, transcript_messages, reconsideration_msg)
                        bot_reply = reconsideration_msg
                        relocation_flag = True
                        continue

            # ends interview if response to relocation question is no AFTER reconsidering, raises flag for hiring manager if answer changes. 
            if relocation_flag:
                if user_input.lower().strip() in ["yes", "yeah", "correct", "that's right"]:
                    final_msg = "Thank you for confirming. Unfortunately, we cannot proceed further since the job requires relocation/commuting."
                    print("Interviewer:", final_msg)
                    bot_reply = final_msg
                    update_history("assistant", conversation_history, transcript_messages, final_msg)
                    write_to_transcript(talent.user.id, talent.user.first_name, messages=transcript_messages)
                    return
                elif user_input.lower().strip() in ["no", "actually, i can", "i changed my mind"]:
                    confirmation_msg = "Thanks for clarifying! Let's move on."
                    print("Interviewer:", confirmation_msg)
                    update_history("assistant", conversation_history, transcript_messages, confirmation_msg)
                    bot_reply = confirmation_msg
                    print(bot_reply.lower())

            update_history("user", conversation_history, transcript_messages, user_input)
            
            try:
                bot_response = get_bot_response(client, conversation_history=conversation_history, tools=[end_interview()])
                bot_reply = bot_response.content
                bot_tools = bot_response.tool_calls
                
                print("Interviewer:", bot_reply)

                update_history("assistant", conversation_history, transcript_messages, bot_reply)

                # Check for function call by model
                # End interview and print summary if found
                if bot_tools:
                    end = False
                    for tool_call in bot_tools:
                        name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)

                        if name == "end_interview":
                            # In a non-terminal version, this would be saved to a database, not shown to interviewee
                            print("\nInterviewer [For admin]:", args["summary"]) 
                            end = True
                    if end:
                        break

            except Exception as e:
                print("Error communicating with OpenAI API:", str(e))


def process_location_update(user_input: str, job_locations: list) -> tuple[str, float]:
    """
    Processes user's location response update during interview

    Inputs:
        user_input (str): location provided by user
        job_locations (list): list of job location objects

    Returns:
        tuple:
            - (str) Updated location or "Invalid" if ignored
            - (float) Updated min distance or set to float("inf") if unknown
    """

    user_input = user_input.strip().lower()

    # ignore invalid location responses
    INVALID_RESPONSES = {"no", "not sure", "maybe", "i don't know", "n/a"}

    if user_input in INVALID_RESPONSES:
        return "Invalid", None 

    matching_location = Location.objects.filter(label__iexact=user_input).first()
    
    if matching_location and matching_location.details:
        updated_lat = matching_location.details.latitude
        updated_lon = matching_location.details.longitude
        print(f"found existing location in database: {matching_location.display_name} ({updated_lat}, {updated_lon})") # remove later
    
        updated_distances = calculate_distance(job_locations, [matching_location])

        if updated_distances: 
            min_dist = min(updated_distances, key=lambda x: x[2])[2]  
            print(f"updated min_dist to {min_dist}") # remove later
        else:
            min_dist = float("inf")

        return matching_location.display_name, min_dist

    else:
        print(f"{user_input} not found in database, defaulting to unknown location")
        return "Unknown", float("inf")
