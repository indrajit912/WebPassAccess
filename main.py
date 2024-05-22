# WebPassAccess - A script that can visit various website
# Author: Indrajit Ghosh
# Created On: Sep 27, 2023
# Modified On: May 21, 2024
# 
# 
import sys
import pyperclip
import webbrowser
import logging
import argparse
import json

from cryptography.fernet import Fernet

from config import *
from mappings import create_site_mapping, create_password_mapping, add_website_to_database, get_user_data
from utils.encryption import sha256, generate_derived_key_from_passwd, encrypt_user_private_key, hash_derived_key, decrypt_user_private_key, encrypt, decrypt
from utils.authentication import get_password, validate_user, generate_session_token, save_session_token, get_existing_session_token, confirm_session_token

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%d-%b-%Y %I:%M:%S %p',
    filename='website_visit.log',
    level=logging.INFO
)

logger = logging.getLogger("WebPassAccess.main")

def _validate_user_and_get_app_key(user_data, password):
    # Validate user
    saved_hashed_passwd = user_data['password_hash']
    if not validate_user(saved_password_hash=saved_hashed_passwd, given_password=password):
        print("Wrong password! Try again later. Exiting...")
        sys.exit()

    # Get derived key
    derived_key = generate_derived_key_from_passwd(password=password)

    # User private key
    encrypted_app_key = user_data['encrypted_app_key']
    app_key = decrypt_user_private_key(derived_key=derived_key, encrypted_private_key=encrypted_app_key)

    return app_key

def visit_site(url:str, passwd:str=None):
    """
    Opens the specified `url` in a web browser and copies the `passwd` to the clipboard.

    Args:
        url (str): The URL of the website to visit.
        passwd (str): The password associated with the website.

    Returns:
        None
    """
    log_msg = (
        f"Opened {url} in the browser."
        if passwd is None
        else
        f"Opened {url} in the browser with password copied in the clipboard."
    )
    if passwd:
        pyperclip.copy(passwd)
    webbrowser.open(url)
    logger.info(log_msg)

def init(args):
    """Initialize the app"""

    if WEBSITES_DATA_JSON.exists():
        print("Already initialized!")
        sys.exit()

    # Create a blank websites_data.json
    blank_data = {"websites": {}}

    # Generate Fernet key
    fernet_key = Fernet.generate_key()

    # Save the session_token
    session_token = generate_session_token(fernet_key)
    save_session_token(token=session_token)

    # Take user's password for the app
    raw_password = get_password()

    # Derive a key from the raw password to encrypt the fernet_key
    derived_key = generate_derived_key_from_passwd(raw_password)

    # Encrypt the fernet key
    encrypted_app_key = encrypt_user_private_key(user_private_key=fernet_key, derived_key=derived_key)

    # Hash the Derive key
    hashed_derived_key = hash_derived_key(derived_key)

    # Add everything to the websites_data.json
    blank_data["encrypted_app_key"] = encrypted_app_key.decode()
    blank_data["derived_key_hash"] = hashed_derived_key
    blank_data["password_hash"] = sha256(raw_password)

    # Save the data
    with open(WEBSITES_DATA_JSON, 'w') as file:
        json.dump(blank_data, file, indent=4)

    print("Database initialized. Now you can add data by using the command `add`.\n")

def add(args):
    password = args.password
    url = args.url
    keys = args.keys
    site_passwd = args.site_password
    site_username = args.site_username

    user_data = get_user_data()
    app_key = _validate_user_and_get_app_key(user_data=user_data, password=password)

    site_passwd_encrypted = encrypt(data=site_passwd, key=app_key)

    add_website_to_database(
        url=url,
        keys=keys,
        password=site_passwd_encrypted,
        username=site_username
    )
    print("Website added successfully!")

def help(args):
    print("USAGE: python3 main.py [command] [options]\n")
    print("COMMANDS:")
    print("  init          Initialize the application")
    print("  add           Add website to configuration")
    print("  visit         Visit an existing website by its key")
    print("  update        Update an existing website data")
    print("  help          Show this help message\n")
    print("For more information on a specific command, use 'python3 main.py [command] --help'")

def visit(args):
    # Get user data
    user_data = get_user_data()

    # Get app_key from session
    existing_session_token = get_existing_session_token()
    app_key = confirm_session_token(token=existing_session_token)
    if not app_key:
        # Invalid session key
        # Ask user for password
        password = input("Session token expired. Enter your app password: ")

        # Verify user
        if not validate_user(saved_password_hash=user_data['password_hash'], given_password=password):
            print("Wrong password! Try again. Exiting...")
        
        # Get the decrypted app_key from database
        encrypted_app_key = user_data['encrypted_app_key']
        derived_key = generate_derived_key_from_passwd(password)
        app_key = decrypt_user_private_key(encrypted_private_key=encrypted_app_key, derived_key=derived_key)
        
        # Generate new session token
        new_token = generate_session_token(app_key)

        # Save the new token
        save_session_token(token=new_token)

    site_mapping, user_data = create_site_mapping()
    password_mapping = create_password_mapping(app_key, user_data)
    site_key = args.site_key

    site_url_hash = site_mapping.get(site_key)
    if site_url_hash is None:
        logger.error(f"Site key '{site_key}' not found in mappings.")
        return

    site_url = user_data['websites'][site_url_hash]['url']
    site_passwd = password_mapping.get(site_url_hash)

    visit_site(url=site_url, passwd=site_passwd)

def update(args):
    password = args.password
    url = args.url
    keys = args.keys
    site_passwd = args.site_password
    site_username = args.site_username

    user_data = get_user_data()

    if not sha256(url) in user_data["websites"].keys():
        print(f"No website with the url '{url}' found! Exiting ...")
        sys.exit()

    app_key = _validate_user_and_get_app_key(user_data=user_data, password=password)

    site_passwd_encrypted = encrypt(data=site_passwd, key=app_key)

    keys = (
        args.keys
        if args.keys
        else user_data["websites"][sha256(url)]["keys"]
    )

    add_website_to_database(
        url=url,
        keys=keys,
        password=site_passwd_encrypted,
        username=site_username
    )
    print("Website updated successfully!")

def main():
    parser = argparse.ArgumentParser(description="CLI Application")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize the application")
    init_parser.set_defaults(func=init)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add website to configuration")
    add_parser.add_argument("--password", "-p", required=True, help="Password for this application that was set during initialization")
    add_parser.add_argument("--url", required=True, help="URL of the website")
    add_parser.add_argument("--keys", nargs="+", required=True, help="List of keys for the website.")
    add_parser.add_argument("--site_password", default=None, help="Password for the website (Optional)")
    add_parser.add_argument("--site_username", default=None, help="Username for the website (Optional)")
    add_parser.set_defaults(func=add)

    visit_parser = subparsers.add_parser("visit", help="Visit an existing website by its key.")
    visit_parser.add_argument("--site_key", required=True, help="Website key")
    visit_parser.set_defaults(func=visit)

    update_parser = subparsers.add_parser("update", help="Update an existing website data.")
    update_parser.add_argument("--password", "-p", required=True, help="Password for this application that was set during initialization")
    update_parser.add_argument("--url", required=True, help="URL of the website to update")
    update_parser.add_argument("--keys", nargs="+", default=None, help="List of keys for the website.")
    update_parser.add_argument("--site_password", default=None, help="Password for the website (Optional)")
    update_parser.add_argument("--site_username", default=None, help="Username for the website (Optional)")
    update_parser.set_defaults(func=update)

    help_parser = subparsers.add_parser("help", help="Help command")
    help_parser.set_defaults(func=help)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
