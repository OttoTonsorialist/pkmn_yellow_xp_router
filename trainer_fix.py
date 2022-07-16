import os
import json

def zhu_li():
    with open('trainers.json', 'r') as f:
        fixed = json.load(f)
    
    with open('trainers_backup.json', 'r') as f:
        loc_fixed = json.load(f)
    
    for key, val in fixed.items():
        val["trainer_location"] = loc_fixed[key]["trainer_location"]
    
    with open('trainers_final.json', 'w') as f:
        json.dump(fixed, f, indent=4)

if __name__ == "__main__":
    zhu_li()