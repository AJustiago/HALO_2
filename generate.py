import json
from datetime import datetime, timedelta
import random

classes = ['plastic', 'metal', 'paper']
start_date = datetime(2025, 4, 11, 8, 0)
data = []

for i in range(100):
    timestamp = start_date + timedelta(minutes=random.randint(0, 7200))  # Random within 5.5 days
    entry = {
        "class": random.choice(classes),
        "timestamp": timestamp.isoformat()
    }
    data.append(entry)

with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)
