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
  def __init__(self, role, api_model, local_model):
    self.role = role
    self.api_model = api_model
    self.local_model = local_model
    self.api_daily_limit_date = None 

  def generate_with_api(self, prompt):
      try:
          response = client.models.generate_content(
              model=self.api_model,
              config=types.GenerateContentConfig(system_instruction=self.role),
              contents=prompt
          )
          return response.text
      except ClientError as e:
          # Check if the error indicates that the daily limit has been hit.
          daily_limit_reached = (int(e.details['error']['details'][0]['violations'][-1]['quotaValue']) == 1500)
          if daily_limit_reached:
              raise DailyLimitException("Daily limit reached")
          
          # If not a daily limit error, determine the retry delay and try again.
          retry_delay = int(e.details['error']['details'][2]['retryDelay'][:-1])
          print(f"Rate limit exceeded. Retrying after {retry_delay} seconds. {e}")
          time.sleep(retry_delay + 1)
          return self.generate_with_api(prompt)

  def generate_locally(self, prompt):
      return ollama.generate(prompt=prompt, system=self.role, model=self.local_model, stream=False)["response"]

  def generate(self, prompt):
      today = datetime.date.today()
      start_time = time.perf_counter()

      # If the API's daily limit has already been reached today, directly use local generation.
      if self.api_daily_limit_date == today:
          result = self.generate_locally(prompt)
      else:
          try:
              result = self.generate_with_api(prompt)
          except DailyLimitException:
              # If the API daily limit is reached during this call, mark today and fall back to local generation.
              print("Daily limit reached. Switching to local generation for the remainder of today.\n")
              self.api_daily_limit_date = today
              result = self.generate_locally(prompt)

      end_time = time.perf_counter()
      duration_seconds = end_time - start_time
      duration_minutes = duration_seconds / 60
      return result, duration_minutes