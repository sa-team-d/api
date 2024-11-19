import os
from re import DEBUG
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from firebase_admin import auth

load_dotenv()

def initialize_firebase():

    # LOAD CREDS FROM DICT OR ENV
    cred = credentials.Certificate({
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    })

    #cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        # print the users in the Firebase project
        if os.getenv("DEBUG"):
            users = auth.list_users()
            for user in users.users:
                print(user.uid)
            # print the roles of the users in the Firebase project
            for user in users.users:
                user = auth.get_user(user.uid)
                print(user.custom_claims)