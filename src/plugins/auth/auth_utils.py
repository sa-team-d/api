import requests
import os
import logging

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("uvicorn.error")

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
debug_mode = os.getenv("DEBUG")

def get_uid_and_token(email: str, password: str):
    """Get the user ID and ID token for a user with the given email and password."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response_data = response.json()
    if "idToken" in response_data:
        if debug_mode: logger.info(f"User {email} signed in successfully with ID token: {response_data['idToken']}")
        return response_data["idToken"], response_data["localId"]
    else:
        raise Exception(f"Error signing in: {response_data.get('error', {}).get('message', 'Unknown error')}")
