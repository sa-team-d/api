import os
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
        users = auth.list_users()
        for user in users.users:
            print(user.uid)
        # print the roles of the users in the Firebase project
        for user in users.users:
            user = auth.get_user(user.uid)
            print(user.custom_claims)

# Function to set the "role" claim to "FFM" for a user with a specific UID
#def set_ffm_role(uid):
#    auth.set_custom_user_claims(uid, {"role": "FFM"})
#    print(f"Role 'FFM' assigned to user with UID: {uid}")
#
## Function to set the "role" claim to "SMO" for a user with a specific UID
#def set_smo_role(uid):
#    auth.set_custom_user_claims(uid, {"role": "SMO"})
#    print(f"Role 'SMO' assigned to user with UID: {uid}")
#
#set_smo_role(os.getenv("FIREBASE_SMO_UID"))
#set_ffm_role(os.getenv("FIREBASE_FFM_UID"))

# Create two users
#uid1 = create_user("ffm@example.com", "passwordffm")
#uid2 = create_user("smo@example.com", "passwordsmo")
#print("UIDs:", uid1, uid2)

