from dotenv import load_dotenv
import os
import django
import signal
import sys
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from interviewer_bot.utils.interview_session import InterviewSession
from interviewer_bot.zoombotrunner import ZoomBotRunner

from profiles.models import TalentProfile
from jobs.models import Job

def receive_response(response : str) -> None:
    '''
    Function Required to run locally via terminal

        Parameters:
            response: str 
                text which will be printed via print function.
        Returns: 
            None
    '''
    print("Interviewer: ", response)

def get_random_job() -> tuple[Job, TalentProfile]:
    '''
    Returns a random Job object and TalentProfile object from the database.

        Parameters:
            None
        Returns: 
            rand_job: Job
                Random Job object from the database 
            rand_talent: TalentProfile
                Random TalentProfile from the database

    '''
    rand_job = Job.objects.order_by('?').first()
    rand_talent = TalentProfile.objects.order_by('?').first()
    print("Conducting a random interview for the position " + rand_job.title +
          ". The candidate's name is " + rand_talent.user.first_name + " " + rand_talent.user.last_name + ".")
    return rand_job, rand_talent

if __name__ == "__main__":
    rand_job, rand_talent = get_random_job()

    # terminal chatbot 
    if len(sys.argv) > 1 and sys.argv[1] == "--terminal":
        interview = InterviewSession(rand_job, rand_talent, receive_response)
        interview.start()
        while not interview.phase == "ENDED":
            i = input("You: ")
            interview.send_response(i)

    # earliest scheduled meeting from calendly
    elif len(sys.argv) > 1 and sys.argv[1] == "--calendly":
        interview = InterviewSession(rand_job, rand_talent)
        runner = ZoomBotRunner(interview, use_calendly=True)

        signal.signal(signal.SIGINT, runner.on_signal)
        signal.signal(signal.SIGTERM, runner.on_signal)
        runner.run()

    # instant meeting  
    else:
        interview = InterviewSession(rand_job, rand_talent)
        runner = ZoomBotRunner(interview)

        # Set up signal handlers
        signal.signal(signal.SIGINT, runner.on_signal)
        signal.signal(signal.SIGTERM, runner.on_signal)
    
        # Run the Meeting Bot
        runner.run()