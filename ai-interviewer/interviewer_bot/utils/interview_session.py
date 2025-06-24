# standard library
import time
import json

# LLM util
from .prompt import *
from .bot import get_client, get_bot_response
from .distances import calculate_distance
from .openai_functions import end_interview, stop_interview_relocation, ask_relocation_confirmation
from .evaluator import evaluate_response_action
from .transcript import write_to_transcript, write_transcript_to_db
from .scoring import score_interview
from .HR_report import generate_report_components

# Django apps and utils
from interviews.models import Interview, InterviewStatusChoices
from profiles.models import TalentProfile
from jobs.models import Job
from django.utils import timezone

class InterviewSession:
    """"
    Interview object for managing interview session
    """
    def __init__(self, job: Job, talent: TalentProfile, response_callback: callable = None):
        """
        InterviewSession constructor
        
        Parameters: 
            job : Job 
                Job object from django database
            talent : TalentProfile 
                TalentProfile object from django database
            response_callback : callable
                function to be called everytime interview wants to send a response
        """
        self.job = job
        self.talent = talent
        self.response_callback = response_callback if response_callback else lambda *args: None
        
        self.client = get_client()
        
        self.transcript_messages = []
        self.conversation_history = []
        self.conversation_history.append({"role": "system", "content": start_interview_prompt(job, talent)})

        self.time_limit = 15 * 60 # 15 minutes
        self.start_time = None
        self.phase = "NOT_STARTED" # NOT_STARTED, LOCATION, RELOCATION_CONFIRM, MAIN, FOLLOWUP, ENDED 
        self.curr_category = None
        
        self.job_locations = self.job.locations.all()
        self.talent_locations = self.talent.locations.all()
        distances = calculate_distance(self.job_locations, self.talent_locations)
        self.min_dist = min(distances, key=lambda x: x[2])[2]  # sort by dist, get min        

        items = list(PROMPT_DICT.items())
        random.shuffle(items)

        self.main_category_iterator = iter(items)
        self.main_question_iterator = None
        self.location_question_iterator = iter(location_prompt(self.min_dist, self.job.remote_option))
        self.category_q_a_pairs = ""
        
    def start(self):
        """"
        Starts the interview
        """
        self.start_time = timezone.now()
        self.interview_object = Interview.objects.create(
            candidate=self.talent, 
            job=self.job,
            start=self.start_time,  # start time
            status=InterviewStatusChoices.SCHEDULED
        )

        self.phase = "LOCATION"
        self.curr_category = "location"
        self.ask_location_question()
    
    def ask_location_question(self):
        """"
        Ask the location questions. After asking location questions, Ask LLM whether relocation question was satisfied. If not, ask reconfirmation, else continue to main questions
        """
        try:
            self.curr_question = next(self.location_question_iterator)
            instruction = f"""You are an ai interviewer, ask the following interview question in a friendly and personalized way. 
            Take the information from their resume to tailor/personalize the questions for the candidate.
            DO NOT ABBREVIATE THE STATE NAME. PRINT THE COMPLETE STATE NAME. 
            Question: {self.curr_question}"""

            self.conversation_history.append({"role": "user", "content": instruction})
            bot_response = get_bot_response(
                self.client, 
                self.conversation_history, 
                tools=[end_interview()]
            )

            if bot_response.content:
                bot_reply = bot_response.content
                self.response_callback(bot_reply)
                self.update_history("assistant", bot_reply)
            else:
                print("Error getting bot_response.content")
        
        except StopIteration:
            # Relocation confirmation part
            
            instruction = f"""If the candidate responded no to the relocation question based on the conversation, call the ask_relocation_confirmation() tool to confirm their relocation decision"""
            
            self.conversation_history.append({"role": "user", "content": instruction})
            bot_response = get_bot_response(self.client, self.conversation_history, tools=[
                                            ask_relocation_confirmation()])

            bot_tools = bot_response.tool_calls
            if bot_tools:
                for tool_call in bot_tools:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    if name == "ask_relocation_confirmation":
                        self.phase = "RELOCATION_CONFIRM"
                        confirmation_question = args["question"]
                        self.update_history("assistant", confirmation_question)
                        self.response_callback(confirmation_question)
                        return
            
            self.phase = "MAIN"
            self.ask_next_main_category()
          
    def confirm_relocation_decision(self):
        """"
        Handle candidate's response to relocation confirmation question
        """
        instruction = f"""Based on the candidate's response, if candidate confirmed they are not willing to relocate, immediately call the stop_interview_relocation tool to end the interview."""
        self.conversation_history.append({"role": "user", "content": instruction})
        bot_response = get_bot_response(
            self.client, 
            self.conversation_history, 
            tools=[stop_interview_relocation()]
        )
        
        if bot_response.content:
            bot_reply = bot_response.content
            self.response_callback(bot_reply)
            self.update_history("assistant", bot_reply)
        
        bot_tools = bot_response.tool_calls
        if bot_tools:
            for tool_call in bot_tools:
                if tool_call.function.name == "stop_interview_relocation":
                    args = json.loads(tool_call.function.arguments)
                    self.finalize_interview()
                    return

        self.phase = "MAIN"
        self.ask_next_main_category()
        
    def ask_next_main_category(self):
        """
        Move to the next category and ask the main question from there. If no more categories, finalize the interview
        """
        try:
            self.curr_category, questions = next(self.main_category_iterator)
            self.main_question_iterator = iter(questions)
            self.ask_next_main_question()
            
        except StopIteration:
            self.finalize_interview()
            
    def ask_next_main_question(self):
        """
        Ask the next main question. If there is no next main question, evaluate responses up to this point and decide whether to followup or move to next category
        """
        try:
            self.curr_question = next(self.main_question_iterator)
            instruction = f"""For your next question, ask the following interview question in a friendly and personalized way. Take the information from their resume to tailor/personalize the questions for the candidate. Before asking the question, provide feedback on previous response given by the user. Question {self.curr_question}"""
            
            self.conversation_history.append({"role": "user", "content": instruction})
            bot_response = get_bot_response(self.client, self.conversation_history, tools=[end_interview()])
            if bot_response.content:
                bot_reply = bot_response.content
                self.response_callback(bot_reply)
                self.update_history("assistant", bot_reply)
                self.category_q_a_pairs += f"Q: {self.curr_question}"

            bot_tools = bot_response.tool_calls
            
            if bot_tools:
                for tool_call in bot_tools:
                    if tool_call.function.name == "end_interview":
                        args = json.loads(tool_call.function.arguments)
                        self.finalize_interview()
    
                        return
                    
        except StopIteration:
            self.evaluate_response()
            
    def evaluate_response(self):
        """
        Evaluate responses based on current category questions. Decides whether to ask followup or reask question.
        """
        action, followup_suggestion = evaluate_response_action(self.client, self.curr_category, self.category_q_a_pairs)
        self.category_q_a_pairs = ""
        if action in ["follow_up", "re_ask"] and followup_suggestion:
            self.curr_question = followup_suggestion
            self.response_callback(followup_suggestion)
            self.update_history("assistant", followup_suggestion)
            self.phase = "FOLLOWUP"
        else:
            self.ask_next_main_category()

    def send_response(self, response : str):
        """
        Recieve response from input and ask question according to current phase
        
        Parameters: 
            response : str 
                Response of user to the previously asked interview question
                
        Returns: 
            None
        """
        
        self.update_history("user", response)
        
        if self.phase == "NOT_STARTED" or self.phase == "ENDED":
            print("Recieved response request. Error: bad phase for response: ", self.phase)
        elif self.phase == "LOCATION":
            self.ask_location_question()
        elif self.phase == "RELOCATION_CONFIRM":
            self.confirm_relocation_decision()
        elif self.phase == "MAIN":
            self.category_q_a_pairs += f"A: {response}\n\n"
            self.ask_next_main_question()
        elif self.phase == "FOLLOWUP":
            self.ask_next_main_category()
        else:    
            print("Error: phase not known: ", self.phase)
    
    def finalize_interview(self):
        """
        Finalizes the interview by marking it as "awaiting feedback", saving the end time,
        and writing the conversation transcript to the database and a jason file.
        """
        
        self.response_callback("Thank you for your responses. The interview has ended. Please wait for our hiring team to contact you for the next steps.")
        
        self.phase = "ENDED"
        self.interview_object.end = timezone.now()
        self.interview_object.status = InterviewStatusChoices.AWAITING_FEEDBACK
        self.interview_object.save()

        write_to_transcript(self.talent.user.id, self.talent.user.first_name, messages=self.transcript_messages)

        write_transcript_to_db(self.interview_object, self.transcript_messages)

        score_interview(self.interview_object, client=self.client)

        generate_report_components(self.interview_object, client=self.client)
        
        
    def update_history(self, role : str, input: str, category: str = None) -> None:
        """
        Update the conversation history and the transcript by adding input into it 

        Parameters: 
            role : str 
                The role of whoever is speaking (user or assistant)
            input : str 
                The inputted message
            category : str 
                The category of the question 
                
        Returns: 
            None
        """
        self.conversation_history.append({"role": role, "content": input})

        message = {"role": role, "content": input, "time": time.strftime("%H:%M:%S", time.localtime())}

        if self.curr_category:
            message["category"] = self.curr_category

        self.transcript_messages.append(message)
