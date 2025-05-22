# chat_simulator.py

import os
import json
import random
import time
import datetime
import ast # For safely evaluating string representation of dict
from agent import agent # Assuming agent.py is in the same directory or path

# --- Configuration ---
SIMULATION_START_TIME_STR = "2023-10-23 00:00:00"
SIMULATION_DURATION_HOURS = 24  # Simulate for 3 hours
SIMULATION_STEP_MINUTES = 5    # Process logic every 1 minute
MAX_MESSAGES = 800              # Stop if this many messages are generated
CHAT_HISTORY_CONTEXT_LENGTH = 25 # How many past messages to feed to the LLM

# Persona activity probabilities (can be tuned)
ACTIVITY_PROB_MAP = {
    "Laag": 0.05,
    "Gemiddeld": 0.15,
    "Hoog": 0.30
}
MENTION_BOOST = 0.5 # Additional probability if mentioned
SPONTANEITY_CHANCE = 0.02 # Base chance to post even without direct triggers

COOLDOWN_MINUTES_BASE = 3 # Base cooldown after posting
COOLDOWN_ACTIVITY_FACTOR = { # Higher activity = shorter cooldown
    "Laag": 1.5,
    "Gemiddeld": 1.0,
    "Hoog": 0.5
}

# LLM Model for chat generation
LOCAL_MODEL_CHAT = "deepseek-r1:7b" # Or your preferred model for chat

# --- Helper Functions ---

def load_personas_from_json_files(persona_files_dir, persona_names_list=None):
    """Loads persona data from JSON files in a directory."""
    personas = {}
    if not os.path.exists(persona_files_dir):
        print(f"Error: Persona directory not found: {persona_files_dir}")
        return personas

    for filename in os.listdir(persona_files_dir):
        if filename.endswith(".json"):
            name_part = filename.replace(".json", "") # Assuming filename is like "John Doe.json"
            # If a specific list of names is provided, only load those
            if persona_names_list and name_part not in persona_names_list:
                continue
            
            filepath = os.path.join(persona_files_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # The JSON directly contains 'Name' and 'bio' string.
                    # We need to parse the 'bio' string to extract structured info for the simulation.
                    # This is a simplification; ideally, the JSON would already be structured.
                    # For now, we assume the JSON directly contains the necessary fields from the augmented CSV.
                    # If your JSON is just {"Name": "X", "bio": "LLM_OUTPUT"}, you need to load from CSV too.
                    # For this example, let's assume the JSON *is* the augmented persona dict:
                    
                    # Placeholder: If your JSONs are just Name+Bio_String, you'd load the full persona
                    # data from the corresponding CSV here and merge.
                    # For this example, we assume the JSON file *is* the augmented persona.
                    # e.g. it was saved as one big JSON per person from the augmented CSV + LLM bio.
                    # If not, you need to adapt this loading.
                    
                    # Initialize simulation-specific state for each persona
                    data['last_read_message_index'] = -1
                    data['message_cooldown_timer'] = 0 # in simulation steps
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
                else: # Slot crosses midnight (e.g., 22:00-02:00)
                    if current_time_obj >= start_time or current_time_obj < end_time:
                        return True
            except ValueError:
                print(f"Warning: Invalid time format in slot '{slot}' for {persona['name']}. Skipping slot.")
        elif isinstance(slot, str) and "gehele dag" in slot.lower() or "sporadisch" in slot.lower(): # Simple catch-alls
            return True # Assume online for these generic terms
    return False


def generate_llm_chat_message(persona, topic, chat_history, chat_agent):
    """Generates a chat message using the LLM agent."""
    # Extract relevant parts from the persona's bio/profile for the prompt
    # The bio JSON should ideally have a pre-generated "Writing style" section.
    # If the bio JSON has Name and a single "bio" string (the LLM output from generate_bio),
    # we need to parse that "bio" string to get the "Writing style" section.
    # For this example, let's assume `persona['Writing style']` exists directly.
    # If not, you'd need to extract it from the `persona['bio']` string.

    # Find the "Writing style:" section in the persona's bio string
    bio_text = persona.get("bio", "") # This is the LLM output from the first script
    writing_style_section = "Schrijft op een gemiddelde manier." # Default
    try:
        # A bit fragile, depends on the exact output format of generate_bio
        start_marker = "**Writing style:**"
        # End marker could be the next section or [END]
        # This simplified extraction assumes "Writing style" is the last section before [END]
        # or before another known section. A more robust parser would be needed for complex bios.
        style_start_index = bio_text.find(start_marker)
        if style_start_index != -1:
            # Attempt to find the end of the writing style section
            # Common next sections could be: [END] or another **Section:**
            # For simplicity, we'll just take a reasonable chunk or up to the next known marker.
            temp_style_text = bio_text[style_start_index + len(start_marker):].strip()
            # Find the end, which could be another section or the end of the string
            end_markers = ["**", "[END]"] # Add other potential section starts if needed
            min_end_idx = len(temp_style_text)
            for marker in end_markers:
                idx = temp_style_text.find(marker)
                if idx != -1 and idx < min_end_idx:
                    min_end_idx = idx
            writing_style_section = temp_style_text[:min_end_idx].strip()
            if not writing_style_section: # if empty after strip
                writing_style_section = "Schrijft op een gemiddelde manier." # Fallback
    except Exception as e:
        print(f"Could not parse writing style for {persona['name']}, using default. Error: {e}")

    persona_prompt_info = f"""
Jouw persona:
- Naam: {persona['name']}
- Leeftijd: {persona.get('age', 'Onbekend')}
- Beroep: {persona.get('job', 'Onbekend')}
- Politieke voorkeur: {persona.get('political_orientation', 'Onbekend')}
- Enkele meningen/overtuigingen (haal uit bio indien beschikbaar, anders algemeen): {persona.get('opinions', 'Geen specifieke meningen bekend.')} 
- Schrijfstijl: {writing_style_section}
"""

    history_str = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in chat_history[-CHAT_HISTORY_CONTEXT_LENGTH:]])
    
    # Determine if it's a reply or a new thought
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
Genereer een korte, natuurlijke chatreactie als jouw persona. Houd je aan je schrijfstijl.
Jouw antwoord:
"""
    # print(f"\n--- Generating for {persona['Name']} ---")
    # print(prompt) # For debugging the prompt

    response_text, duration = chat_agent.generate(prompt)
    # print(f"LLM ({duration:.2f}m): {response_text}")
    
    # Basic cleaning: LLMs sometimes add "Persona Name:" prefix
    cleaned_response = response_text.strip()
    if cleaned_response.lower().startswith(f"{persona['name'].lower()}:"):
        cleaned_response = cleaned_response[len(persona['name'])+1:].strip()
    
    return cleaned_response


# --- Main Simulation Logic ---

def run_simulation(personas_data, topic, chat_agent):
    chat_log = []
    current_sim_time = datetime.datetime.strptime(SIMULATION_START_TIME_STR, "%Y-%m-%d %H:%M:%S")
    simulation_end_time = current_sim_time + datetime.timedelta(hours=SIMULATION_DURATION_HOURS)
    
    simulation_step_delta = datetime.timedelta(minutes=SIMULATION_STEP_MINUTES)
    num_simulation_steps = 0

    # --- Initial Seed Message ---
    # Find active personas to select one for the initial seed
    online_at_start = []
    for name, p_data in personas_data.items():
        print(name, p_data)
        if is_persona_online(p_data, current_sim_time):
            online_at_start.append(name)
    
    if online_at_start:
        seed_poster_name = random.choice(online_at_start)
        seed_poster = personas_data[seed_poster_name]
        # For seed, we can use topic's initial prompt or let LLM generate based on topic
        # Option 1: Use topic seed directly
        # seed_message_text = topic['initial_prompt_seed']
        # Option 2: Let LLM generate an opening statement based on the topic (more natural)
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


    # --- Simulation Loop ---
    while current_sim_time < simulation_end_time and len(chat_log) < MAX_MESSAGES:
        print(f"\n--- Time: {current_sim_time.strftime('%Y-%m-%d %H:%M')} (Step {num_simulation_steps}) ---")
        new_messages_this_step = False

        # Update persona online status and cooldowns
        online_names = []
        for name, p_data in personas_data.items():
            p_data['is_online'] = is_persona_online(p_data, current_sim_time)
            if p_data['is_online']:
                online_names.append(name)
            if p_data['message_cooldown_timer'] > 0:
                p_data['message_cooldown_timer'] -= 1
        print(f"  Online this step: {online_names}")


        # Determine who might post
        potential_posters = []
        for name, p_data in personas_data.items():
            if not p_data['is_online'] or p_data['message_cooldown_timer'] > 0:
                continue

            # Basic probability based on activity level
            prob_to_post = ACTIVITY_PROB_MAP.get(p_data.get("Chat Activity Level", "Gemiddeld"), 0.1)
            
            # Did they see new messages?
            # (Simplified: if new messages exist since they last read/posted)
            if p_data['last_read_message_index'] < len(chat_log) -1:
                # Increase chance if new messages are relevant (not by them)
                if chat_log[-1]['sender'] != name:
                    prob_to_post += 0.1 # Generic "engagement" boost

            # Check for mentions
            was_mentioned = False
            # Check last few messages for a direct @mention
            for msg_idx in range(max(0, len(chat_log) - 3), len(chat_log)):
                 if f"@{name}" in chat_log[msg_idx]['text']: # Simple @mention check
                    was_mentioned = True
                    break
            if was_mentioned:
                prob_to_post += MENTION_BOOST

            # Spontaneity / Proactive post
            prob_to_post += SPONTANEITY_CHANCE
            
            # Max probability of 1.0
            prob_to_post = min(prob_to_post, 1.0)

            # print(f"  {name}: Prob to post = {prob_to_post:.2f}")
            if random.random() < prob_to_post:
                potential_posters.append(name)
        
        # If multiple want to post, select one (e.g., randomly, or based on who was mentioned)
        if potential_posters:
            # Prioritize mentioned people slightly
            mentioned_posters = [p for p in potential_posters if any(f"@{p}" in msg['text'] for msg in chat_log[-3:])]
            if mentioned_posters:
                poster_name = random.choice(mentioned_posters)
            else:
                poster_name = random.choice(potential_posters)
            
            persona_to_post = personas_data[poster_name]

            # Generate message
            message_text = generate_llm_chat_message(persona_to_post, topic, chat_log, chat_agent)
            
            if message_text: # Ensure LLM returned something
                chat_log.append({
                    "id": len(chat_log),
                    "timestamp": current_sim_time.isoformat(),
                    "sender": poster_name,
                    "text": message_text,
                    "topic_id": topic['id']
                })
                print(f"[{current_sim_time.strftime('%H:%M')}] {poster_name}: {message_text}")
                new_messages_this_step = True

                # Update poster's state
                cooldown_factor = COOLDOWN_ACTIVITY_FACTOR.get(persona_to_post.get("Chat Activity Level", "Gemiddeld"), 1.0)
                persona_to_post['message_cooldown_timer'] = int(COOLDOWN_MINUTES_BASE * cooldown_factor / SIMULATION_STEP_MINUTES)
                persona_to_post['last_read_message_index'] = len(chat_log) -1

        if not new_messages_this_step:
            print("  No new messages this step.")

        current_sim_time += simulation_step_delta
        num_simulation_steps += 1
        time.sleep(0.1) # Small delay to make output readable, not for simulation accuracy

    return chat_log


if __name__ == "__main__":
    # --- Setup ---
    # 1. Define Personas to participate
    #    This path should point to where your individual persona JSON files are.
    #    Example: if you have group_1.json, group_2.json etc.
    #    And group_1.json contains a list of persona objects for that group.
    #    OR, if you have data/bios_json/group_1/John Doe.json, data/bios_json/group_1/Jane Smith.json
    
    # For this example, let's assume a flat directory of persona JSON files.
    # You'll need to adapt this to your actual persona storage.
    # This path should lead to where your JSON files for *one specific chat group* are stored.
    # Each JSON file is assumed to be one persona's full data (including augmented fields).
    
    # IMPORTANT: Adapt this path to where your persona JSONs for ONE GROUP are.
    # Example: 'data/bios_json/group_1_bios_json/'
    # The `load_personas_from_json_files` function expects individual JSON files per persona in this directory.
    PERSONA_JSON_DIR = 'data/bios/group_1' # Placeholder - CHANGE THIS
                                          # This should be the folder containing the JSON outputs
                                          # from your first script (after running it on an augmented CSV).
                                          # e.g., data/bios/group_1.json -> then you'd parse this main JSON
                                          # OR data/bios/group_1_jsons/Maria.json, data/bios/group_1_jsons/Piet.json

    # If your main bios are saved as one big JSON per group (e.g., group_1.json has a list of bios)
    # you'll need to modify `load_personas_from_json_files` or pre-process it.
    # For now, it assumes individual .json files per persona within PERSONA_JSON_DIR.

    # Let's try to make `load_personas_from_json_files` more robust for a single group JSON file:
    def load_personas_from_group_json(group_json_filepath):
        personas = {}
        if not os.path.exists(group_json_filepath):
            print(f"Error: Group JSON file not found: {group_json_filepath}")
            return personas
        else:
            print(f"Loading personas from group JSON file: {group_json_filepath}")
        try:
            with open(group_json_filepath, 'r', encoding='utf-8') as f:
                # The file is a list of dicts, each dict has "Name" and "bio" string.
                data_list = json.load(f) 
                for p_data_entry in data_list:
                    # Here, p_data_entry is {"Name": "X", "bio": "LLM_OUTPUT_STRING"}
                    # We need the *original augmented CSV data* for simulation parameters
                    # like "Typical Online Hours", "Chat Activity Level", etc.
                    # The "bio" string itself is for the LLM to know how to write, not for sim params.
                    
                    # THIS IS A CRITICAL POINT: The current `generate_bio` and `save_bio`
                    # only save Name + the LLM-generated bio string.
                    # For the simulator, we need the full augmented persona profile.
                    #
                    # SOLUTION:
                    # 1. Modify `save_bio` to save the *entire row (persona data from CSV)*
                    #    along with the LLM-generated bio string, perhaps nested.
                    #    e.g., {"Name": "X", "profile_data": {all_csv_fields...}, "llm_bio_text": "..."}
                    # 2. OR, during chat simulation loading, re-load the original CSV for the group
                    #    and merge its data with the loaded bio (matching by Name).
                    #
                    # For now, I will assume you've modified `save_bio` so that the JSON entry
                    # for each persona *already contains all the augmented CSV fields*.
                    # If `p_data_entry` is already the full persona dict, then:
                    
                    # Let's assume p_data_entry is already the full dict:
                    name = p_data_entry.get("name")
                    if not name:
                        print("Skipping entry without a Name in group JSON.")
                        continue

                    # Initialize simulation-specific state
                    p_data_entry['last_read_message_index'] = -1
                    p_data_entry['message_cooldown_timer'] = 0
                    p_data_entry['is_online'] = False
                    # The "bio" key contains the LLM-generated text.
                    # Other keys like "Typical Online Hours" should be top-level in p_data_entry
                    personas[name] = p_data_entry
                    print(f"Loaded persona: {name} from group JSON.")

        except Exception as e:
            print(f"Error loading personas from {group_json_filepath}: {e}")
        if not personas:
            print(f"No personas loaded from {group_json_filepath}.")
        return personas

    # --- Point to your group's JSON file that contains a LIST of persona objects ---
    # --- Each object in the list should be a FULL persona profile (not just Name+Bio) ---
    GROUP_BIO_JSON_FILEPATH = 'data/bios/group_1.json' # <<<<  YOU MUST CREATE/HAVE THIS FILE

    active_personas = load_personas_from_group_json(GROUP_BIO_JSON_FILEPATH)

    if not active_personas:
        print("Exiting: No personas loaded for simulation.")
        exit()

    # 2. Define Topic
    current_topic = {
        "id": "topic_002",
        "title": "Nieuw parkeergebied",
        "description": "De gemeente heeft plannen voor een nieuw parkeergebied aan de rand van het dorp. Wat vinden we hiervan?"
    }

    # 3. Initialize Chat Agent
    #    The role here is for generating chat messages, not bios.
    chat_agent_role = (
        "Jij bent een deelnemer in een online groepschat. "
        "Je reageert op basis van je toegewezen persona en de chatgeschiedenis. "
        "Formuleer je antwoorden als een normaal chatbericht. "
        "Voeg GEEN extra uitleg of commentaar toe buiten het chatbericht zelf."
    )
    chat_llm_agent = agent(role=chat_agent_role, local_model=LOCAL_MODEL_CHAT)

    # 4. Run Simulation
    print("\nStarting chat simulation...")
    start_sim_wall_time = time.time()
    
    generated_chat_log = run_simulation(active_personas, current_topic, chat_llm_agent)
    
    end_sim_wall_time = time.time()
    print(f"\nSimulation finished in {end_sim_wall_time - start_sim_wall_time:.2f} seconds (wall time).")

    # 5. Save Chat Log
    output_chatlog_file = f"data/chat_logs/chatlog_{current_topic['id']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_chatlog_file), exist_ok=True)
    with open(output_chatlog_file, 'w', encoding='utf-8') as f:
        json.dump(generated_chat_log, f, indent=2, ensure_ascii=False)
    print(f"Chat log saved to: {output_chatlog_file}")