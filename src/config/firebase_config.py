import os
from re import DEBUG
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from firebase_admin import auth

load_dotenv()

def initialize_firebase():
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
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