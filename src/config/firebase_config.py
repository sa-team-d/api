import os
from re import DEBUG
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

FIREBASE_TYPE = os.getenv("FIREBASE_TYPE")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI")
FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI")
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
FIREBASE_CLIENT_X509_CERT_URL = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")

def initialize_firebase():

    # LOAD CREDS FROM DICT OR ENV
    # cred = credentials.Certificate({
    #     "type": f"{FIREBASE_TYPE}",
    #     "project_id": f"{FIREBASE_PROJECT_ID}",
    #     "private_key_id": f"{FIREBASE_PRIVATE_KEY_ID}",
    #     "private_key": f"{FIREBASE_PRIVATE_KEY}",
    #     "client_email": f"{FIREBASE_CLIENT_EMAIL}",
    #     "client_id": f"{FIREBASE_CLIENT_ID}",
    #     "auth_uri": f"{FIREBASE_AUTH_URI}",
    #     "token_uri": f"{FIREBASE_TOKEN_URI}",
    #     "auth_provider_x509_cert_url": f"{FIREBASE_AUTH_PROVIDER_X509_CERT_URL}",
    #     "client_x509_cert_url": f"{FIREBASE_CLIENT_X509_CERT_URL}"
    # })
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        # print the users in the Firebase project
        if os.getenv("DEBUG"):
            users = firebase_admin.auth.list_users()
            for user in users.users:
                print(user.uid)
            # print the roles of the users in the Firebase project
            for user in users.users:
                user = auth.get_user(user.uid)
                print(user.custom_claims)