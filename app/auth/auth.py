from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import json
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "users.json")


def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def list_all_users():
    users = load_users()

    return [
        {
            "username": username,
            "role": user["role"],
            "departments": user["departments"]
        }
        for username, user in users.items()
    ]


def add_user(username, password, role, departments):
    users = load_users()

    if username in users:
        return False

    users[username] = {
        "hashed_password": hash_password(password),
        "role": role,
        "departments": departments
    }

    save_users(users)
    return True


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password):
    return pwd_context.hash(plain_password)


def authenticate_user(username, password):
    users = load_users()
    user = users.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return {"username": username, "role": user["role"], "departments": user["departments"]}


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    users = load_users()
    user = users.get(username)
    if user is None:
        raise credentials_exception
    return {"username": username, "role": user["role"], "departments": user["departments"]}


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def update_user_departments(username, departments):
    users = load_users()
    if username not in users:
        return False
    users[username]["departments"] = departments
    save_users(users)
    return True

def signup_user(username, password):
    users = load_users()

    if username in users:
        return False

    users[username] = {
        "hashed_password": hash_password(password),
        "role": "employee",
        "departments": []
    }

    save_users(users)
    return True