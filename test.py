import pandas as pd
import json
import os

# Define the directories
json_dir = "data/bios"
csv_dir = "data/groups"

# Iterate through JSON files in the directory
for json_file in os.listdir(json_dir):
    if json_file.endswith(".json"):
        # Construct file paths
        json_path = os.path.join(json_dir, json_file)
        csv_path = os.path.join(csv_dir, json_file.replace(".json", ".csv"))
        
        # Check if corresponding CSV file exists
        if os.path.exists(csv_path):
            # Load JSON data
            with open(json_path, 'r') as f:
                json_data = json.load(f)
            
            # Load CSV data
            csv_data = pd.read_csv(csv_path)
            
            # Compare lengths
            if len(json_data) != len(csv_data):
                print(f"Mismatch in file lengths: {json_file}")
                os.remove(json_path)
