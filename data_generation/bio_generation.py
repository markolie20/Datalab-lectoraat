import os, json, time
import pandas as pd
from agent import agent


def generate_bio(row, bio_agent):
    row_dict = row.to_dict()

    toh = row_dict.get("typical_online_hours", {})
    if isinstance(toh, str):
        try:
            toh = json.loads(toh)
        except Exception:
            toh = {"weekdays": [], "weekends": []}
    props = {
      "Name": row_dict.get("name"),
      "Age": row_dict.get("age"),
      "Gender": row_dict.get('sex'),
      "Birthdate": str(row_dict.get("birthdate", "N/A")), 

      "Occupation": row_dict.get("job", "N/A"),
      "Company": row_dict.get("company", "N/A"),
      "Education Level": row_dict.get("education_level", "N/A"),
      "Country": "Netherland", # Het gaat over mensen die in nederland wonen
      "Country of Origin": row_dict.get("country_of_origin", "N/A"),
      "Residence": row_dict.get("residence", "N/A"),
      "Socio-Economic Class": row_dict.get("socio_economic_status", "N/A"),
      "Income Level": row_dict.get("income_level", "N/A"),
      "Employment Status": row_dict.get("employment_status", "N/A"),
      "Marital Status": row_dict.get("marital_status", "N/A"),
      "Household Composition": row_dict.get("household_composition", "N/A"),
      "Housing Type": row_dict.get("housing_type", "N/A"),
      "Religion": row_dict.get("religion", "N/A"),
      "Political Orientation": row_dict.get("political_orientation", "N/A"),
      "Health Status": row_dict.get("health_status", "N/A"),

      "Technological Proficiency": row_dict.get("technology_proficiency", "N/A"),
      "Website": str(row_dict.get("website", "N/A")), 
      "Username": row_dict.get("username", "N/A"),

      "Chat Activity Level": row_dict.get("activity_level", "N/A"),
      "Typical Online Hours": str(row_dict.get("typical_online_hours", "N/A")), 
      "Chat Response Latency": row_dict.get("response_latency_profile", "N/A"),
      "Emoji Usage Propensity": row_dict.get("emoji_usage_propensity", "N/A"),
      "Mention Propensity in Chat": row_dict.get("mention_propensity", "N/A"),
      "Preferred Message Length": row_dict.get("message_length_preference", "N/A"),
      "Punctuation Habits in Chat": row_dict.get("punctuation_habits", "N/A"),
      "Spelling Error Frequency in Chat": row_dict.get("spelling_error_frequency", "N/A"),
      "Grammar Correctness in Chat": row_dict.get("grammar_correctness", "N/A"),
      "Typical Language Style in Chat": row_dict.get("language_style", "N/A"),
      "Emphasis Style in Chat": row_dict.get("emphasis_style", "N/A"),
      "Message Chaining Preference": row_dict.get("message_chaining_preference", "N/A")
    }
    properties_list = [f"- {key}: {value}" for key, value in props.items() if value is not None]
    properties_string = "\n".join(properties_list)

    instruction_text = "Create a bio for the person detailed below. The bio should include a general description, their norms and values, beliefs, opinions, and a description of their typical chat writing style. Base the 'Writing style' section on their chat behavior attributes."
    format_string = """
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
    prompt = f"Instruction: {instruction_text}\n\nPersona Details:\n{properties_string}\n\nFormatting of the answer (your response must follow this exact format and structure, including all specified headers like **Description:**, **Normen en Waarden:**, etc.):\n{format_string}"
    
    response, duration = bio_agent.generate(prompt)
    print(f'Bio generated for {row_dict.get("name", "Unknown")} in {duration:.2f} minutes')
    return response


def save_bio(df, bio_agent, filepath):
    bios_data_list = []
    start_time_total = time.perf_counter()

    for index, row in df.iterrows():
        try:
            persona_profile = row.to_dict()
            toh = persona_profile.get("typical_online_hours")
            if isinstance(toh, str):
                try:
                    persona_profile["typical_online_hours"] = json.loads(toh.replace("'", '"'))       
                except Exception as e:
                    print(f"Warning: Could not parse typical_online_hours for {persona_profile.get('name', 'unknown')}: {e}")
                    persona_profile["typical_online_hours"] = {"weekdays": [], "weekends": []}

            llm_bio_string_with_markers = generate_bio(row, bio_agent) 
            
            start_marker = "[START]"
            end_marker = "[END]"
            start_idx = llm_bio_string_with_markers.find(start_marker)
            end_idx = llm_bio_string_with_markers.find(end_marker)

            if start_idx != -1 and end_idx != -1:
                bio_content_only = llm_bio_string_with_markers[start_idx + len(start_marker):end_idx].strip()
            else:
                print(f"Warning: Could not find [START]/[END] markers for {row['name']}. Using full response.")
                bio_content_only = llm_bio_string_with_markers.strip()

            persona_profile['llm_generated_bio_text'] = bio_content_only 
            bios_data_list.append(persona_profile)

        except Exception as e:
            print(f"Error processing bio for {row['name']}: {str(e)}")
        
    end_time_total = time.perf_counter()
    duration_minutes = (end_time_total - start_time_total) / 60
    print(f'All bios for ({filepath}) processed in {duration_minutes:.2f} minutes\n')
    
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(bios_data_list, fp=file, indent=4, ensure_ascii=False)


def generate_bios():
  BIO_DATA_FOLDER = 'data/bios'
  GROUP_DATA_FOLDER = 'data/groups'
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
    local_model=LOCAL_MODEL)
  
  for csv_file in os.listdir(GROUP_DATA_FOLDER)[:9]:
    csv_filepath = os.path.join(GROUP_DATA_FOLDER, csv_file)
    df = pd.read_csv(csv_filepath)

    json_file = csv_file.replace('.csv', '.json')
    json_filepath = os.path.join(BIO_DATA_FOLDER, json_file)

    if os.path.exists(json_filepath):
      print(f'{json_filepath} already exists, skipping')
      continue
    
    save_bio(df, bio_agent, json_filepath)
    
    
if __name__ == "__main__":
    generate_bios()