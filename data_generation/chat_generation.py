import os
import json
import random
import time
import datetime
import ast 
from agent import agent 

SIMULATION_START_TIME_STR = "2023-10-23 00:00:00"
SIMULATION_DURATION_HOURS = 24  
SIMULATION_STEP_MINUTES = 5  
MAX_MESSAGES = 800           
CHAT_HISTORY_CONTEXT_LENGTH = 25 

ACTIVITY_PROB_MAP = {
    "Laag": 0.05,
    "Gemiddeld": 0.15,
    "Hoog": 0.30
}
MENTION_BOOST = 0.5
SPONTANEITY_CHANCE = 0.02 

COOLDOWN_MINUTES_BASE = 3 
COOLDOWN_ACTIVITY_FACTOR = {
    "Laag": 1.5,
    "Gemiddeld": 1.0,
    "Hoog": 0.5
}

def load_personas_from_json_files(persona_files_dir, persona_names_list=None):
    """Loads persona data from JSON files in a directory."""
    personas = {}
    if not os.path.exists(persona_files_dir):
        print(f"Error: Persona directory not found: {persona_files_dir}")
        return personas

    for filename in os.listdir(persona_files_dir):
        if filename.endswith(".json"):
            name_part = filename.replace(".json", "")
            if persona_names_list and name_part not in persona_names_list:
                continue
            
            filepath = os.path.join(persona_files_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['last_read_message_index'] = -1
                    data['message_cooldown_timer'] = 0
                    data['is_online'] = False
                    personas[data['name']] = data
                    print(f"Loaded persona: {data['name']}")
            except Exception as e:
                print(f"Error loading persona {filename}: {e}")
    if not personas:
        print(f"No personas loaded. Check directory and persona_names_list: {persona_files_dir}")
    return personas


def parse_online_hours(online_hours_str):
    """Safely parses the string representation of typical_online_hours."""
    try:
        return ast.literal_eval(online_hours_str)
    except (ValueError, SyntaxError):
        print(f"Warning: Could not parse online_hours: {online_hours_str}. Defaulting to always offline.")
        return {"weekdays": [], "weekends": []}


def is_persona_online(persona, current_sim_time):
    online_hours_data = persona.get("typical_online_hours", {})
    
    day_type = "weekends" if current_sim_time.weekday() >= 5 else "weekdays"
    time_slots = online_hours_data.get(day_type, [])

    current_time_obj = current_sim_time.time()

    for slot in time_slots:
        if isinstance(slot, str) and '-' in slot:
            try:
                start_str, end_str = slot.split('-')
                start_time = datetime.datetime.strptime(start_str.strip(), "%H:%M").time()
                end_time = datetime.datetime.strptime(end_str.strip(), "%H:%M").time()

                if start_time <= end_time:
                    if start_time <= current_time_obj < end_time:
                        return True
                else:
                    if current_time_obj >= start_time or current_time_obj < end_time:
                        return True
            except ValueError:
                print(f"Warning: Invalid time format in slot '{slot}' for {persona['name']}. Skipping slot.")
        elif isinstance(slot, str) and "gehele dag" in slot.lower() or "sporadisch" in slot.lower():
            return True
    return False


def generate_llm_chat_message(persona, topic, chat_history, chat_agent):
    """Generates a chat message using the LLM agent."""
    bio_text = persona.get("bio", "") 
    writing_style_section = "Schrijft op een gemiddelde manier." 
    try:
        start_marker = "**Writing style:**"
        style_start_index = bio_text.find(start_marker)
        if style_start_index != -1:
            temp_style_text = bio_text[style_start_index + len(start_marker):].strip()
            end_markers = ["**", "[END]"] 
            min_end_idx = len(temp_style_text)
            for marker in end_markers:
                idx = temp_style_text.find(marker)
                if idx != -1 and idx < min_end_idx:
                    min_end_idx = idx
            writing_style_section = temp_style_text[:min_end_idx].strip()
            if not writing_style_section: 
                writing_style_section = "Schrijft op een gemiddelde manier." 
    except Exception as e:
        print(f"Could not parse writing style for {persona['name']}, using default. Error: {e}")
    persona_prompt_info = f"""
Jouw persona:
- Naam: {persona['name']}
- Leeftijd: {persona['age']}
- Geslacht: {persona['sex']}
- Geboortedatum: {persona['birthdate']}
- Land van herkomst: {persona['country_of_origin']}
- Sociaal-economische status: {persona['socio_economic_status']}
- Huishoudsamenstelling: {persona['household_composition']}
- Politieke oriëntatie: {persona['political_orientation']}
- Opleidingsniveau: {persona['education_level']}
- Religie: {persona['religion']}
- Burgerlijke staat: {persona['marital_status']}
- Werkstatus: {persona['employment_status']}
- Woningtype: {persona['housing_type']}
- Technologische vaardigheid: {persona['technology_proficiency']}
- Gezondheidsstatus: {persona['health_status']}
- Inkomensniveau: {persona['income_level']}
- Activiteitsniveau: {persona['activity_level']}
- Typische online uren: {persona['typical_online_hours']}
- Reactievertraging: {persona['response_latency_profile']}
- Emoji-gebruik: {persona['emoji_usage_propensity']}
- Mention-gedrag: {persona['mention_propensity']}
- Voorkeur berichtlengte: {persona['message_length_preference']}
- Interpunctie-gewoonten: {persona['punctuation_habits']}
- Spelfoutfrequentie: {persona['spelling_error_frequency']}
- Grammaticale correctheid: {persona['grammar_correctness']}
- Taalstijl: {persona['language_style']}
- Nadrukstijl: {persona['emphasis_style']}
- Berichtketen-voorkeur: {persona['message_chaining_preference']}
- Beroep: {persona['job']}
- Normen en waarden: {persona.get('normen_en_waarden', 'Niet gespecificeerd')}
- Overtuigingen: {persona.get('beliefs', 'Niet gespecificeerd')}
- Meningen: {persona.get('opinions', 'Niet gespecificeerd')}
- Schrijfstijl: {writing_style_section}
"""

    history_str = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in chat_history[-CHAT_HISTORY_CONTEXT_LENGTH:]])

    instruction_hint = "Reageer op de laatste berichten of start een nieuwe gedachte gerelateerd aan het onderwerp."
    if chat_history and chat_history[-1]['sender'] != persona['name']:
        instruction_hint = f"Reageer op het gesprek, met name op {chat_history[-1]['sender']} indien relevant."
    if any(f"@{persona['name']}" in msg['text'] for msg in chat_history[-3:]): # Mentioned recently
         instruction_hint = f"Je bent genoemd (@{persona['name']}). Reageer hierop of op de algemene discussie."

    prompt = f"""{persona_prompt_info}
Huidig gespreksonderwerp: {topic['title']} - {topic['description']}

Recente chatgeschiedenis (laatste {CHAT_HISTORY_CONTEXT_LENGTH} berichten):
{history_str if history_str else "Nog geen berichten."}

Instructie: {instruction_hint}
Genereer een natuurlijke chatreactie als jouw persona. Houd je aan je schrijfstijl, meningen en voorkeuren.

Let op: Blijf altijd volledig trouw aan je persona, ook als dit betekent dat je het oneens bent met anderen, het gesprek een andere wending geeft, of je mening herhaalt. Je mag gerust meningsverschillen uiten, van onderwerp wisselen als dat bij je persona past, of reageren op een manier die typerend is voor jouw karakter. jouw antwoorden moeten altijd authentiek zijn voor jouw persona, zelfs als dat leidt tot discussie, misverstanden of onverwachte wendingen in het gesprek. Gebruik je eigen stijl, voorkeuren en overtuigingen zoals beschreven in je profiel.

Jouw antwoord:
"""
    response_text, duration = chat_agent.generate(prompt)
    cleaned_response = response_text.strip()
    if cleaned_response.lower().startswith(f"{persona['name'].lower()}:"):
        cleaned_response = cleaned_response[len(persona['name'])+1:].strip()
    
    return cleaned_response

def run_simulation(personas_data, topic, chat_agent):
    chat_log = []
    current_sim_time = datetime.datetime.strptime(SIMULATION_START_TIME_STR, "%Y-%m-%d %H:%M:%S")
    simulation_end_time = current_sim_time + datetime.timedelta(hours=SIMULATION_DURATION_HOURS)
    
    simulation_step_delta = datetime.timedelta(minutes=SIMULATION_STEP_MINUTES)
    num_simulation_steps = 0
    online_at_start = []
    for name, p_data in personas_data.items():
        print(name, p_data)
        if is_persona_online(p_data, current_sim_time):
            online_at_start.append(name)
    
    if online_at_start:
        seed_poster_name = random.choice(online_at_start)
        seed_poster = personas_data[seed_poster_name]
        seed_prompt = f"""
Jouw persona:
- Naam: {seed_poster['name']}
- Schrijfstijl: {seed_poster.get('writing style', 'normaal')}

Huidig gespreksonderwerp: {topic['title']} - {topic['description']}
Instructie: Start het gesprek over dit onderwerp met een openingsbericht of vraag.
Jouw antwoord:
"""
        seed_message_text, _ = chat_agent.generate(seed_prompt)
        if seed_message_text.lower().startswith(f"{seed_poster_name.lower()}:"):
            seed_message_text = seed_message_text[len(seed_poster_name)+1:].strip()

        chat_log.append({
            "id": len(chat_log),
            "timestamp": current_sim_time.isoformat(),
            "sender": seed_poster_name,
            "text": seed_message_text,
            "topic_id": topic['id']
        })
        print(f"[{current_sim_time.strftime('%H:%M')}] {seed_poster_name}: {seed_message_text} (SEED)")
        seed_poster['message_cooldown_timer'] = int(COOLDOWN_MINUTES_BASE * COOLDOWN_ACTIVITY_FACTOR.get(seed_poster.get("Chat Activity Level", "Gemiddeld"), 1.0) / SIMULATION_STEP_MINUTES)
        seed_poster['last_read_message_index'] = len(chat_log) - 1
    else:
        print("No personas online at start to seed message. Waiting for someone to come online.")

    while current_sim_time < simulation_end_time and len(chat_log) < MAX_MESSAGES:
        print(f"\n--- Time: {current_sim_time.strftime('%Y-%m-%d %H:%M')} (Step {num_simulation_steps}) ---")
        new_messages_this_step = False

        online_names = []
        for name, p_data in personas_data.items():
            p_data['is_online'] = is_persona_online(p_data, current_sim_time)
            if p_data['is_online']:
                online_names.append(name)
            if p_data['message_cooldown_timer'] > 0:
                p_data['message_cooldown_timer'] -= 1
        print(f"  Online this step: {online_names}")

        potential_posters = []
        for name, p_data in personas_data.items():
            if not p_data['is_online'] or p_data['message_cooldown_timer'] > 0:
                continue

            prob_to_post = ACTIVITY_PROB_MAP.get(p_data.get("Chat Activity Level", "Gemiddeld"), 0.1)
            
            if p_data['last_read_message_index'] < len(chat_log) -1:
                if chat_log[-1]['sender'] != name:
                    prob_to_post += 0.1 

            was_mentioned = False
            for msg_idx in range(max(0, len(chat_log) - 3), len(chat_log)):
                 if f"@{name}" in chat_log[msg_idx]['text']:
                    was_mentioned = True
                    break
            if was_mentioned:
                prob_to_post += MENTION_BOOST

            prob_to_post += SPONTANEITY_CHANCE

            prob_to_post = min(prob_to_post, 1.0)

            if random.random() < prob_to_post:
                potential_posters.append(name)
        
        if potential_posters:
            mentioned_posters = [p for p in potential_posters if any(f"@{p}" in msg['text'] for msg in chat_log[-3:])]
            if mentioned_posters:
                poster_name = random.choice(mentioned_posters)
            else:
                poster_name = random.choice(potential_posters)
            
            persona_to_post = personas_data[poster_name]

            message_text = generate_llm_chat_message(persona_to_post, topic, chat_log, chat_agent)
            
            if message_text: 
                chat_log.append({
                    "id": len(chat_log),
                    "timestamp": current_sim_time.isoformat(),
                    "sender": poster_name,
                    "text": message_text,
                    "topic_id": topic['id']
                })
                print(f"[{current_sim_time.strftime('%H:%M')}] {poster_name}: {message_text}")
                new_messages_this_step = True

                cooldown_factor = COOLDOWN_ACTIVITY_FACTOR.get(persona_to_post.get("Chat Activity Level", "Gemiddeld"), 1.0)
                persona_to_post['message_cooldown_timer'] = int(COOLDOWN_MINUTES_BASE * cooldown_factor / SIMULATION_STEP_MINUTES)
                persona_to_post['last_read_message_index'] = len(chat_log) -1

        if not new_messages_this_step:
            print("  No new messages this step.")

        current_sim_time += simulation_step_delta
        num_simulation_steps += 1
        time.sleep(0.1)

    return chat_log


def load_personas_from_group_json(group_json_filepath):
    personas = {}
    if not os.path.exists(group_json_filepath):
        print(f"Error: Group JSON file not found: {group_json_filepath}")
        return personas
    else:
        print(f"Loading personas from group JSON file: {group_json_filepath}")
    try:
        with open(group_json_filepath, 'r', encoding='utf-8') as f:
            data_list = json.load(f) 
            for p_data_entry in data_list:
                name = p_data_entry.get("name")
                if not name:
                    print("Skipping entry without a Name in group JSON.")
                    continue

                p_data_entry['last_read_message_index'] = -1
                p_data_entry['message_cooldown_timer'] = 0
                p_data_entry['is_online'] = False
                personas[name] = p_data_entry
                print(f"Loaded persona: {name} from group JSON.")

    except Exception as e:
        print(f"Error loading personas from {group_json_filepath}: {e}")
    if not personas:
        print(f"No personas loaded from {group_json_filepath}.")
    return personas


LOCAL_MODEL_CHAT = "deepseek-r1:7b" 
CHAT_AGENT_ROLE = (
    "Jij bent een deelnemer in een online groepschat. "
    "Je reageert op basis van je toegewezen persona en de chatgeschiedenis. "
    "Formuleer je antwoorden als een normaal chatbericht. "
    "Voeg GEEN extra uitleg of commentaar toe buiten het chatbericht zelf."
)
CHAT_LLM_AGENT = agent(role=CHAT_AGENT_ROLE, local_model=LOCAL_MODEL_CHAT)

PERSONA_JSON_DIR = 'data/bios/group_1'
TOPICS =  [ {
    "id": "topic_002",
    "title": "Nieuw parkeergebied",
    "description": "De gemeente heeft plannen voor een nieuw parkeergebied aan de rand van het dorp. Wat vinden we hiervan?"
}, 
{
    "id": "topic_003",
    "title": "Verkeersveiligheid",
    "description": "Hoe kunnen we de verkeersveiligheid in ons dorp verbeteren?"
},
{
    "id": "topic_004",
    "title": "Groene energie",
    "description": "Wat vinden we van de plannen voor meer groene energie in onze regio?"
},
{
    "id": "topic_005",
    "title": "Onderwijsvernieuwing",
    "description": "Hoe kunnen we het onderwijs in onze gemeente verbeteren?"
},
{
    "id": "topic_006",
    "title": "Woningbouwprojecten",
    "description": "Wat vinden we van de nieuwe woningbouwprojecten in onze regio?"
}
,
{
    "id": "topic_007",
    "title": "Lokale economie",
    "description": "Hoe kunnen we de lokale economie stimuleren?"
},
{
    "id": "topic_008",
    "title": "Cultuur en evenementen",
    "description": "Welke culturele evenementen moeten we organiseren in ons dorp?"
},
{
    "id": "topic_009",
    "title": "Milieu en duurzaamheid",
    "description": "Wat kunnen we doen om het milieu te beschermen in onze regio?"
}
,
{
    "id": "topic_010",
    "title": "Gezondheidszorg",
    "description": "Hoe kunnen we de gezondheidszorg in onze gemeente verbeteren?"
}
]

def generate_chatlogs(bios_folder='data/bios'):
    """Generates chat logs for all personas in the specified folder."""
    if not os.path.exists(bios_folder):
        print(f"Error: Bios folder not found: {bios_folder}")
        return
    for bios_json in os.listdir(bios_folder):
        if bios_json.endswith('.json'):
            print(f"Found bios json file: {bios_json}")
        personas = load_personas_from_json_files(bios_folder, bios_json)
        if not personas:
            print("No personas loaded. Exiting.")
            return
            
        for topic in TOPICS:
            print(f"\nStarting simulation for topic: {topic['title']}")
            start_sim_wall_time = time.time()
            chat_log = run_simulation(personas, topic, CHAT_LLM_AGENT)
            end_sim_wall_time = time.time()
            sim_time = end_sim_wall_time - start_sim_wall_time
            print(f"Simulation complete. Generated {len(chat_log)} messages, in {sim_time:.2f} seconds.")

            output_chatlog_file = f"data/chat_logs/chatlog_{topic['id']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(output_chatlog_file), exist_ok=True)
            with open(output_chatlog_file, 'w', encoding='utf-8') as f:
                json.dump(chat_log, f, indent=2, ensure_ascii=False)
            print(f"Chat log saved to: {output_chatlog_file}")

def generate_chatlogs(group_json_filepath='data/bios/group_1.json'):
    """Generates chat logs for all personas in the specified group JSON file."""
    if not os.path.exists(group_json_filepath):
        print(f"Error: Group JSON file not found: {group_json_filepath}")
        return

    personas = load_personas_from_group_json(group_json_filepath)
    if not personas:
        print("No personas loaded. Exiting.")
        return

    for topic in TOPICS:
        print(f"\nStarting simulation for topic: {topic['title']}")
        start_sim_wall_time = time.time()
        chat_log = run_simulation(personas, topic, CHAT_LLM_AGENT)
        end_sim_wall_time = time.time()
        sim_time = end_sim_wall_time - start_sim_wall_time
        print(f"Simulation complete. Generated {len(chat_log)} messages, in {sim_time:.2f} seconds.")

        output_chatlog_file = f"data/chat_logs/chatlog_{topic['id']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_chatlog_file), exist_ok=True)
        with open(output_chatlog_file, 'w', encoding='utf-8') as f:
            json.dump(chat_log, f, indent=2, ensure_ascii=False)
        print(f"Chat log saved to: {output_chatlog_file}")
        
if __name__ == "__main__":
    for json_file in os.listdir('data/bios'):
        if json_file.endswith('.json'):
            json_path = os.path.join('data/bios', json_file)
            generate_chatlogs(json_path)