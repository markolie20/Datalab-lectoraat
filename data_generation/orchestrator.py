from bio_generation import generate_bios
from chat_generation import generate_chatlogs
import os
for json_file in os.listdir('data/bios'):
    if json_file.endswith('.json'):
        json_path = os.path.join('data/bios', json_file)
        generate_chatlogs(json_path)