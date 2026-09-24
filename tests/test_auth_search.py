import requests

BASE_URL = "http://localhost:8000"


def login(username, password):
    response = requests.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password}
    )
    response.raise_for_status()
    return response.json()["access_token"]


def ask(question, token):
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"question": question},
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# Test 1: owner (admin, sees everything) asks an IT question
# ============================================================
print("="*60)
print("TEST 1: owner (admin) asks about IT password policy")
print("="*60)

owner_token = login("owner", "Owner@123")
result = ask("What is the minimum password length required?", owner_token)
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}\n")


# ============================================================
# Test 2: hr.sara (HR only) asks the SAME IT question
# ============================================================
print("="*60)
print("TEST 2: hr.sara (HR-only access) asks the SAME IT question")
print("="*60)

hr_token = login("hr.sara", "Hr@12345")
result = ask("What is the minimum password length required?", hr_token)
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}\n")


# ============================================================
# Test 3: hr.sara asks an HR question (should work normally)
# ============================================================
print("="*60)
print("TEST 3: hr.sara asks an HR question (should work fine)")
print("="*60)

result = ask("How many vacation days do I get?", hr_token)
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}\n")