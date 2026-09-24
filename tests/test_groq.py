import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Read the API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("[ERROR] API key not found. Check your .env file")
else:
    print("[OK] API key loaded successfully")

    # Create Groq client
    client = Groq(api_key=api_key)

    # Send a simple test message
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": "Hello ."}
        ]
    )

    print("\n[MODEL RESPONSE]")
    print(response.choices[0].message.content)