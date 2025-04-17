import os
import pandas as pd
import json
import time
from agent import agent

def generate_bio(row, bio_agent):
    props = {
      "Name": row["name"],
      "Age": row["age"],
      "Gender": row['sex'],
      "Occupation": row["job"],
      "Country": "Netherlands",
      "Country of Origin": row["country_of_origin"],
      "Socio-Economic Class": row["socio_economic_status"],
      "Household Composition": row["household_composition"],
      "Political Orientation": row["political_orientation"],
      "Education Level": row["education_level"],
      "Religion": row["religion"],
      "Marital Status": row["marital_status"],
      "Employment Status": row["employment_status"],
      "Housing Type": row["housing_type"],
      "Technological Proficiency": row["technology_proficiency"],
      "Health Status": row["health_status"]
    }
    instruction = f"Create a bio for a person with the following properties: {props}" 
    format = """
Your response must follow exactly the format below, and nothing else should appear outside the delimiters:

[START]
**Description:** 
A description of their life in a paragraph of 5 to 6 sentences.

**Normen en Waarden:** 
-**value**: description

**Beliefs:**
-**belief**: description

**Opinions:**
-**opinion**: description

**Writing style:**
A description of how this person would write chats
[END]

Do not add any additional text, comments, or headers.

Example:
[START]
**Description:**
Jane Doe — Jane is a 34-year-old teacher from Amsterdam who has overcome many challenges in her life. She has dedicated her career to advocating for education and community reform. With a passion for art and literature, Jane spends her free time volunteering and leading local cultural projects. Her life has been a journey marked by hard work, perseverance, and a continuous desire to learn.

**Norms and Values:**
- **Integrity:** Jane values honesty and transparency in every aspect of her life.
- **Compassion:** She deeply cares for the well-being of her community.
- **Respect:** Jane believes in treating everyone with fairness and dignity.
- **Responsibility:** She holds herself accountable for the impact her actions have on others.

**Beliefs:**
- **Empowerment through Education:** Jane believes that education is the cornerstone of personal growth and community development.
- **Community Solidarity:** She holds that collective action and mutual aid can overcome societal challenges.
- **Environmental Stewardship:** Jane believes in the importance of sustainable living and protecting natural resources.

**Opinions:**
- **Government Involvement:** Jane is of the opinion that governments should invest more in public education and healthcare.
- **Social Equity:** She thinks policies should prioritize reducing inequality and providing equal opportunities for all citizens.
- **Cultural Enrichment:** Jane opines that supporting the arts and cultural initiatives is vital for a dynamic, forward-thinking society.

**Writing style:**
Jane writes in a short, coherent manners. She doesn't really use punctuation while chatting and sometimes makes spelling mistakes.
[END]
"""
    prompt = f"Instruction:{instruction}\n\nFormatting of the answer(json):{format}"
    response, duration = bio_agent.generate(prompt)
    print(f'Bio generated for {row["name"]} in {duration:.2f} minutes')
    return response

def save_bio(df, bio_agent, filepath):
    bios = []
    start_time = time.perf_counter()
    for index, row in df.iterrows():
      try:
        formatted_bio = generate_bio(row, bio_agent)  # Assuming this function is defined
        start_marker = "[START]"
        end_marker = "[END]"
        start_index = formatted_bio.find(start_marker) + len(start_marker)
        end_index = formatted_bio.find(end_marker)
        bio_content = formatted_bio[start_index:end_index].strip()

        bio_entry = {
            "Name": df.iloc[index]['name'],
            "bio": bio_content
        }
        bios.append(bio_entry)

      except Exception as e:
          print(f"Error formatting bio for {row['name']}: {str(e)}")
          continue
      
    end_time = time.perf_counter()
    duration_seconds = end_time - start_time
    duration_minutes = duration_seconds / 60
    print(f'Bios ({filepath}) generated in {duration_minutes:.2f} minutes\n')
    # Save the list of bios to a JSON file
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(bios, fp=file, indent=4)

def main():
  BIO_DATA_FOLDER = 'data/bios'
  GROUP_DATA_FOLDER = 'data/groups'
  API_MODEL = "gemini-2.0-flash"
  LOCAL_MODEL = "deepseek-r1:7b"

  os.makedirs(BIO_DATA_FOLDER, exist_ok=True)

  if not os.path.exists(GROUP_DATA_FOLDER):
     raise FileNotFoundError(f'{GROUP_DATA_FOLDER} not found, please make sure path is correct')
   
  bio_agent = agent(
    role=(
      "You are a perfectly written Python program without bugs. "
      "You strictly follow the given format and do not deviate from it. "
      "You do not add any extra headers, introductory sentences, or comments. "
      "You only provide the output in the exact format requested, without any additional text or modifications."
    ),
    api_model=API_MODEL, local_model=LOCAL_MODEL)
  
  for csv_file in os.listdir(GROUP_DATA_FOLDER):
    csv_filepath = os.path.join(GROUP_DATA_FOLDER, csv_file)
    df = pd.read_csv(csv_filepath)

    json_file = csv_file.replace('.csv', '.json')
    json_filepath = os.path.join(BIO_DATA_FOLDER, json_file)

    if os.path.exists(json_filepath):
      print(f'{json_filepath} already exists, skipping')
      continue
    
    save_bio(df, bio_agent, json_filepath)

if __name__ == '__main__':
  main()