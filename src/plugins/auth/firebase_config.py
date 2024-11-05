import firebase_admin
from firebase_admin import credentials
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

# Function to set the "role" claim to "FFM" for a user with a specific UID
def set_ffm_role(uid):
    auth.set_custom_user_claims(uid, {"role": "FFM"})
    print(f"Role 'FFM' assigned to user with UID: {uid}")

# Function to set the "role" claim to "SMO" for a user with a specific UID
def set_smo_role(uid):
    auth.set_custom_user_claims(uid, {"role": "SMO"})
    print(f"Role 'SMO' assigned to user with UID: {uid}")

# Create two users
#uid1 = create_user("ffm@example.com", "passwordffm")
#uid2 = create_user("smo@example.com", "passwordsmo")

uid1 = "k8SM6PwrJ4g663v5uZo8gfC7iND2"
uid2 = "xM2kea8akaOKvYta26NMFBy8YnJ3"

set_smo_role(uid1)
set_ffm_role(uid2)

print("UIDs:", uid1, uid2)