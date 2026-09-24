# reset_password.py — حطيه في نفس مستوى create_users.py وشغله مرة واحدة
import json
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_FILE = os.path.join("data", "users.json")  # عدلي المسار لو مختلف

username = "owner"
new_password = "Admin123!"  # غيريه لباسورد تحبيه

with open(USERS_FILE, "r", encoding="utf-8") as f:
    users = json.load(f)

users[username]["hashed_password"] = pwd_context.hash(new_password)

with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2)

print(f"Password for '{username}' updated to: {new_password}")