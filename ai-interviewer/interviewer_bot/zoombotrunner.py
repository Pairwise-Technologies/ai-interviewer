import gi
import os
import time
from dotenv import load_dotenv
from gi.repository import GLib

from .meetingbot import MeetingBot
from .meeting import Meeting
from .utils.interview_session import InterviewSession

gi.require_version('GLib', '2.0')

class ZoomBotRunner:
    '''Runs the zoom bot'''
    def __init__(self, interview : InterviewSession, use_calendly=False):

        self.interview = interview

        self.use_calendly = use_calendly
        self.bot = None
        self.meeting = None
        self.main_loop = None
        self.shutdown_requested = False
        self.timeout = 600

    def exit_process(self):
        '''Clean shutdown of the bot and main loop'''
        print("Starting cleanup process...")
        
        # Set flag to prevent re-entry
        if self.shutdown_requested:
            return False
        self.shutdown_requested = True
        
        try:


            if self.bot:
                print("Leaving meeting...")
                self.bot.leave()
                print("Cleaning up bot...")
                self.bot.cleanup()
            
            if self.meeting:
                self.meeting.end_zoom_meeting()
                # self.meeting.delete_zoom_meeting() # instant meetings are deleted once ended
            
            self.force_exit()

        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.force_exit()
        
        return False

    def force_exit(self):
        '''Force the process to exit'''
        print("Forcing exit...")
        os._exit(0)  # Use os._exit() to force immediate termination
        return False

    def on_signal(self, signum, frame):
        '''Signal handler for SIGINT and SIGTERM'''
        print(f"\nReceived signal {signum}")
        self.bot.shutdown = True
        # Schedule the exit process to run soon, but not immediately
        if self.main_loop:
            GLib.timeout_add(100, self.exit_process)
        else:
            self.exit_process()

    def on_timeout(self):
        '''Regular timeout callback'''
        if self.shutdown_requested:
            return False
        return True

    def timer(self):
        '''Finds out if the bot is alone or not, if it is for timeout amount of time it will cause the bot to leave'''
        alone = self.bot.alone
        start = self.bot.start_time
        if alone != None and start != None:
            if alone and time.time() - start >= self.timeout:
                self.exit_process()
        return True 
    
    def run(self):
        '''Main run method'''
        self.meeting = Meeting()

        if self.use_calendly: # get link of meeting created by calendly

            if not self.meeting.meeting_from_calendly(): 
                print("Meeting failed to load from Calendly.")
                self.exit_process()
                return

            print("Meeting loaded from Calendly! Link:", self.meeting.join_url)

        else:  #creates meeting and get link 
    
                try:
                    self.meeting.create_zoom_meeting()
                except Exception as e:
                    print(e)
                    self.exit_process()
                
                if self.meeting.meeting_id == None:
                    print("meeting failed to create")
                    self.exit_process()
                    return
                
                print("Meeting created! Link: ", self.meeting.join_url)



        
        self.bot = MeetingBot(self.meeting.meeting_id, self.meeting.encrypted_password, self.interview)
        
        try:
            self.bot.init()
        except Exception as e:
            print(e)
            self.exit_process()

        # Create a GLib main loop
        self.main_loop = GLib.MainLoop()

        # Add a timeout function that will be called every 100ms
        GLib.timeout_add(100, self.on_timeout)
        GLib.timeout_add_seconds(1, self.timer)

        try:
            print("Starting main event loop")
            self.main_loop.run()
        except KeyboardInterrupt:
            print("Interrupted by user, shutting down...")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.exit_process()