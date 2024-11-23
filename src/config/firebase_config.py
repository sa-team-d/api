import os
from re import DEBUG
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

import sys
sys.path.append('.')

load_dotenv()

FIREBASE_TYPE = os.getenv("FIREBASE_TYPE")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n')
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI")
FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI")
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
FIREBASE_CLIENT_X509_CERT_URL = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")

def initialize_firebase():
    cred = credentials.Certificate({
        "type": f"{FIREBASE_TYPE}",
        "project_id": f"{FIREBASE_PROJECT_ID}",
        "private_key_id": f"{FIREBASE_PRIVATE_KEY_ID}",
        "private_key": f"{FIREBASE_PRIVATE_KEY}",
        "client_email": f"{FIREBASE_CLIENT_EMAIL}",
        "client_id": f"{FIREBASE_CLIENT_ID}",
        "auth_uri": f"{FIREBASE_AUTH_URI}",
        "token_uri": f"{FIREBASE_TOKEN_URI}",
        "auth_provider_x509_cert_url": f"{FIREBASE_AUTH_PROVIDER_X509_CERT_URL}",
        "client_x509_cert_url": f"{FIREBASE_CLIENT_X509_CERT_URL}"
    })
    #cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        # print the users in the Firebase project
        if os.getenv("DEBUG"):
            users = firebase_admin.auth.list_users()
            for user in users.users:
                print(user.uid)
            for user in users.users:
                user = firebase_admin.auth.get_user(user.uid)
                print(user.custom_claims)