import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.auth.auth import hash_password

users = {
    "owner": {
        "hashed_password": hash_password("Owner@123"),
        "role": "admin",
        "departments": ["ALL"]
    },
    "hr.sara": {
        "hashed_password": hash_password("Hr@12345"),
        "role": "employee",
        "departments": ["HR"]
    },
    "it.omar": {
        "hashed_password": hash_password("It@12345"),
        "role": "employee",
        "departments": ["IT"]
    }
}

os.makedirs("data", exist_ok=True)
with open("data/users.json", "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2)

print("Created users:")
for username, info in users.items():
    print(f"  {username} -> role: {info['role']}, departments: {info['departments']}")