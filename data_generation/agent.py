import os
import time
import datetime
import ollama
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from dotenv import load_dotenv

from custom_exceptions import DailyLimitException

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

class agent():
    def __init__(self, role, local_model="deepseek-r1:7b"):
        self.role = role
        self.api_model = "gemini-2.0-flash-lite"
        self.local_model = local_model
        self.api_daily_limit_date = None 
        self.api_daily_limit = 1500

    def generate_with_api(self, prompt):
        try:
            response = client.models.generate_content(
                    model=self.api_model,
                    config=types.GenerateContentConfig(system_instruction=self.role),
                    contents=prompt
                )
            return response.text
        except ClientError as e:
            try:
                daily_limit_reached = (int(e.details['error']['details'][0]['violations'][-1]['quotaValue']) == 1500)
                if daily_limit_reached:
                    raise DailyLimitException("Daily limit reached")
                retry_delay = int(e.details['error']['details'][2]['retryDelay'][:-1])
                print(f"Rate limit exceeded. Retrying after {retry_delay} seconds.")
                time.sleep(retry_delay + 1)
                return self.generate_with_api(prompt)
                
            except Exception as e:
                response = self.generate_locally(prompt)
                return response

    def generate_locally(self, prompt):
        return ollama.generate(prompt=prompt, system=self.role, model=self.local_model, stream=False)["response"]

    def generate(self, prompt):
        today = datetime.date.today()
        start_time = time.perf_counter()

        if self.api_daily_limit_date == today:
            result = self.generate_locally(prompt)
        else:
            try:
                result = self.generate_with_api(prompt)
            except DailyLimitException:
                print("Daily limit reached for the Gemini API (1500 requests per day). Switching to local generation for the remainder of today.\n")
                self.api_daily_limit_date = today
                result = self.generate_locally(prompt)

        end_time = time.perf_counter()
        duration_seconds = end_time - start_time
        duration_minutes = duration_seconds / 60
        return result, duration_minutes
  
class PersonaAgent(agent):
    def __init__(self, *args, activity_rate=4, response_delay=(5,60),
                 reaction_chance=0.3, online_rate, **kwargs):
        super().__init__(*args, **kwargs)
        # avg # messages per hour when online:
        self.activity_rate = activity_rate  
        # (min,max) seconds to respond once they're “triggered”
        self.response_delay = response_delay  
        # chance they’ll react to someone else’s post
        self.reaction_chance = reaction_chance
        # chance they will go online or offline
        self.online_rate = online_rate