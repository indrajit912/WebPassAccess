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
from constants import SECRET_KEY

SALT = "terminal_session_token_from_user_master_passwd_hash"
EXPIRATION = 3600 * 3  # 3 hours in seconds

def get_session_token(master_passwd_hash):
    """
    Generate a session token using the master password hash.
    
    :param master_passwd_hash: The hash of the user's master password.
    :return: The generated session token.
    """
    serializer = URLSafeTimedSerializer(
        secret_key=SECRET_KEY, salt=SALT
    )
    return serializer.dumps({'master_passwd_hash': master_passwd_hash})


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

        master_passwd_hash = data.get('master_passwd_hash')

        if master_passwd_hash is not None:
            return {'master_passwd_hash': master_passwd_hash}
        else:
            return None  # Invalid token structure

    except itsdangerous.SignatureExpired:
        return None  # Token expired

    except itsdangerous.BadSignature:
        return None  # Invalid token
