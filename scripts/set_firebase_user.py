from firebase_admin import auth, initialize_app
from firebase_admin.credentials import Certificate
import os
from dotenv import load_dotenv

load_dotenv()

cred = Certificate(os.getenv("FIREBASE_CREDENTIALS"))
initialize_app(cred)

# Function to create a user and return their UID
def create_user(email: str, password: str):
    user = auth.create_user(email=email, password=password)
    print(f"Created user with UID: {user.uid}")
    return user.uid

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
