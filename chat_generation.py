import os
import ollama
import pandas as pd

GROUP_FOLDER = 'data/groups'
TEST_GROUP = os.path.join(GROUP_FOLDER, 'group_1.csv')
MODEL = "deepseek-r1:7b"

df = pd.read_csv(TEST_GROUP)
print(df.head())

class agent():
  def __init__(self, role, model="llama3.1"):
    self.role = role
    self.model = model
  def generate(self, prompt):
    return ollama.generate(prompt=prompt, system=self.role, model=self.model, stream=False)["response"]

bio_agent = agent(
  role=(
    "You are a perfectly written Python program without bugs. "
    "You strictly follow the given format and do not deviate from it. "
    "You do not add any extra headers, introductory sentences, or comments. "
    "You only provide the output in the exact format requested, without any additional text or modifications."
  ),
  model=MODEL
)

def generate_bio(row):
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
**Name:** 
A description of their life in a paragraph of 5 to 6 sentences.

**Normen en Waarden:** 
-**value**: description

**Beliefs:**
-**belief**: description

**Opinions:**
-**opinion**: description
[END]

Do not add any additional text, comments, or headers.

Example:
[START]
**Name:**
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
[END]
"""
    prompt = f"Instruction:{instruction}\n\nFormatting of the answer(json):{format}"
    return bio_agent.generate(prompt)
print(df.columns)

with open("bios.md", "w", encoding="utf-8") as file:
  for index, row in df.iterrows():
    bio = generate_bio(row)
    start_index = bio.find("[START]") + len("[START]")
    end_index = bio.find("[END]")
    if start_index != -1 and end_index != -1:
      formatted_bio = bio[start_index:end_index].strip()
      file.write(formatted_bio + "\n\n")
    else:
      print(f"Formatting issue in bio for {row['name']}")
