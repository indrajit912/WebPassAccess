"""
Session Token Generation and Verification Script

Author: Indrajit Ghosh
Created On: May 22, 2024

This script provides functions to generate and verify session tokens based on a user's master password hash.
Session tokens are used for user authentication and authorization in secure applications.

Functions:
    - get_session_token(master_passwd_hash): Generates a session token using the provided master password hash.
    - confirm_session_token(token, expiration): Confirms the validity of a session token within a specified expiration time.

Usage Example:
    1. Generate a session token using the user's master password hash.
    2. Store the session token securely.
    3. When needed, verify the session token to authenticate the user.

Dependencies:
    - itsdangerous library for secure token serialization and deserialization.

Note: Ensure to keep the SECRET_KEY secret and protect session tokens from unauthorized access.
"""

from itsdangerous import URLSafeTimedSerializer
import itsdangerous
import pwinput
from config import SECRET_KEY, DOT_SESSION_TOKEN_FILE
from utils.encryption import sha256

SALT = "terminal_session_token_from_user_master_passwd_hash"
EXPIRATION = 3600 * 3  # 3 hours in seconds

def get_password():
    bullet_unicode = '\u2022'
    while True:
        password1 = pwinput.pwinput("Enter your password: ", mask=bullet_unicode)
        password2 = input("Confirm your password: ")
        if password1 == password2:
            print("Password set successfully!")
            return password1
        else:
            print("Passwords do not match. Please try again.")

def validate_user(saved_password_hash, given_password):
    return sha256(given_password) == saved_password_hash

def generate_session_token(decrypted_app_key):
    """
    Generate a session token using the master password hash.
    
    :param master_passwd_hash: The hash of the user's master password.
    :return: The generated session token.
    """
    if isinstance(decrypted_app_key, bytes):
        decrypted_app_key = decrypted_app_key.decode()

    serializer = URLSafeTimedSerializer(
        secret_key=SECRET_KEY, salt=SALT
    )
    return serializer.dumps({'app_key': decrypted_app_key})


def confirm_session_token(token: str, expiration: int = EXPIRATION):
    """
    Confirm the validity of a session token.
    
    :param token: The session token to be confirmed.
    :param expiration: The expiration time for the token in seconds (default 1 hour).
    :return: If the token is valid, return the decoded data, otherwise return None.
    """
    serializer = URLSafeTimedSerializer(
        secret_key=SECRET_KEY, salt=SALT
    )

    try:
        data = serializer.loads(token, max_age=expiration)

        app_key = data.get('app_key')

        if app_key is not None:
            return app_key
        else:
            return None  # Invalid token structure

    except itsdangerous.SignatureExpired:
        return None  # Token expired

    except itsdangerous.BadSignature:
        return None  # Invalid token


def save_session_token(token:str):
    """Save the session token"""
    with open(DOT_SESSION_TOKEN_FILE, 'w') as f:
        f.write(token)

def get_existing_session_token():
    """Get the existing session token from the file"""
    if not DOT_SESSION_TOKEN_FILE.exists():
        return None
    
    with open(DOT_SESSION_TOKEN_FILE, 'r') as f:
        return f.read()


