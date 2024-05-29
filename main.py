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
import pwinput

from cryptography.fernet import Fernet

from config import *
from functions import create_site_mapping, create_password_username_mapping, add_website_to_database, get_user_data, save_user_data, clear_screen
from utils.encryption import sha256, generate_derived_key_from_passwd, encrypt_user_private_key, hash_derived_key, decrypt_user_private_key, encrypt, decrypt
from utils.authentication import get_password, validate_user, generate_session_token, save_session_token, get_existing_session_token, confirm_session_token
from utils.bash_utilities import add_wpa_command_aliases_to_bashrc


# logging.basicConfig(
#     format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
#     datefmt='%d-%b-%Y %I:%M:%S %p',
#     filename='webpassaccess.log',
#     level=logging.INFO
# )

# logger = logging.getLogger("WebPassAccess.main")

# # Set the root logger level to CRITICAL
# logging.basicConfig(level=logging.CRITICAL)

# # Disable all logging for other loggers and handlers
# logging.disable(logging.CRITICAL)


def _input_password(info_msg:str="Enter your password: "):
    return pwinput.pwinput(info_msg, mask=BULLET_UNICODE)

def _validate_user_and_get_app_key(user_data, password):
    # Validate user
    saved_hashed_passwd = user_data['password_hash']
    if not validate_user(saved_password_hash=saved_hashed_passwd, given_password=password):
        # logger.error("Wrong password! Exiting...")
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
    # logger.info(log_msg)

def init(args):
    """Initialize the app"""

    if WEBSITES_DATA_JSON.exists():
        # logger.error("Database already initialized!")
        print("Already initialized!")
        sys.exit()

    # Create app_data dir
    if not APP_DATA_DIR.exists():
        APP_DATA_DIR.mkdir()

    # Create a blank websites_data.json
    blank_data = {"websites": {}}

    # Generate Fernet key
    fernet_key = Fernet.generate_key()

    # Save the session_token
    session_token = generate_session_token(fernet_key)
    save_session_token(token=session_token)

    # Take user's password for the app
    raw_password = get_password(
        info_msg="Enter a password for this app (e.g- you could enter the system password!): "
    )

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
    
    add_wpa_command_aliases_to_bashrc()

    print("Database initialized. Now you can add data by using the command `add`.\n")
    # logger.info("Database initialized!")


def _setup_passwd_and_username_args(args, user_data):

    # Checking if the app password is correct
    if args.password:
        password = _input_password(info_msg="[-] Enter the app password: ")
    else:
        # logger.error("No password provided.")
        print("[Error] No password provided. Use the flag '-p'.")
        sys.exit()

    # Get the app_key
    app_key = _validate_user_and_get_app_key(user_data=user_data, password=password)

    # Setting up optional args
    if args.site_password:
        site_passwd = get_password(
            info_msg="\n[-] Enter the password for the given website: ",
            success_msg="The password has been saved successfully along with the website url to the database.\n"
        )
        site_passwd_encrypted = encrypt(data=site_passwd, key=app_key)
    else:
        site_passwd_encrypted = None

    if args.site_username:
        site_username = input("[-] Enter the username for the website: ")
    else:
        site_username = None

    return site_passwd_encrypted, site_username

def add(args):
    # Getting user data
    user_data = get_user_data()

    site_passwd_encrypted, site_username = _setup_passwd_and_username_args(args=args, user_data=user_data)

    add_website_to_database(
        url=args.url,
        keys=args.keys,
        password=site_passwd_encrypted,
        username=site_username
    )
    # logger.info("Website added successfully!")
    print("Website added successfully!")

def visit(args):
    # Get user data
    user_data = get_user_data()

    # Get app_key from session
    existing_session_token = get_existing_session_token()
    app_key = confirm_session_token(token=existing_session_token)
    if not app_key:
        # Invalid session key
        # Ask user for password
        password = pwinput.pwinput("Session token expired. Enter your app password: ", mask=BULLET_UNICODE)

        # Verify user
        if not validate_user(saved_password_hash=user_data['password_hash'], given_password=password):
            # logger.error("Wrong password! Exiting...")
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
    password_username_mapping = create_password_username_mapping(app_key, user_data)
    site_key = args.site_key

    site_url_hash = site_mapping.get(site_key)
    if site_url_hash is None:
        # logger.error(f"Site key '{site_key}' not found in mappings.")
        print(f"Site key '{site_key}' not found in mappings.")
        return

    site_url = user_data['websites'][site_url_hash]['url']
    site_info = password_username_mapping.get(site_url_hash)

    visit_site(url=site_url, passwd=site_info['password'])

def delete_site(args):
    # Getting user data
    user_data = get_user_data()
    key_to_del = args.site_key

    found = False
    for url_hash, website_info in user_data['websites'].items():
        if key_to_del in website_info['keys']:
            del user_data['websites'][url_hash]
            save_user_data(user_data)
            print("Website data deleted successfully!")
            return

    if not found:
        print(f"No website found with the key '{key_to_del}'")

def update(args):
    # Getting user data
    user_data = get_user_data()

    # Check whether the url exists in the db
    url=args.url
    if not sha256(url) in user_data["websites"].keys():
        # logger.error(f"No website with the url '{url}' found! Exiting ...")
        print(f"No website with the url '{url}' found! Exiting ...")
        sys.exit()

    site_passwd_encrypted, site_username = _setup_passwd_and_username_args(args=args, user_data=user_data)

    # Setting up keys
    keys = args.keys
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
    # logger.info("Website updated successfully!")
    print("Website updated successfully!")


def show_db(args):
    # Get user data
    data = get_user_data()

    clear_screen()
    print("======================================")
    print("Website Information:")
    print("======================================")
    sp = "     - "
    count = 1
    for _, website in data["websites"].items():
        print(f"[{count}] URL: {website['url']}")
        if 'username' in website:
            print(f"{sp}Username: {website['username']}")
        if 'password' in website:
            print(f"{sp}Password: [encrypted]")
        print(f"{sp}Keys: {', '.join(website['keys'])}")
        print()
        count +=1


def search(args):
    data = get_user_data()

    site_key = args.site_key

    clear_screen()
    print("======================================")
    print("Website Information:")
    print("======================================")
    sp = "     - "

    for _, website in data["websites"].items():
        if site_key in website['keys']:
            print(f"[-] URL: {website['url']}")
            if 'username' in website:
                print(f"{sp}Username: {website['username']}")
            if 'password' in website:
                print(f"{sp}Password: [encrypted]")
            print(f"{sp}Keys: {', '.join(website['keys'])}")
            print()
            break


def help(args):
    print("USAGE: python3 main.py [command] [options]\n")
    print("COMMANDS:")
    print("  init          Initialize the application")
    print("  db            Display all saved website data")
    print("  add           Add website to configuration")
    print("  visit         Visit an existing website by its key")
    print("  update        Update an existing website data")
    print("  del           Delete an existing website data")
    print("  search        Search an existing website data")
    print("  help          Show this help message\n")
    print("For more information on a specific command, use 'python3 main.py [command] --help'")


def main():
    # Check if the initialization file exists
    init_required = not WEBSITES_DATA_JSON.exists()

    parser = argparse.ArgumentParser(description="CLI Application")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize the application")
    init_parser.set_defaults(func=init)

    if not init_required:
        # Show db command
        show_parser = subparsers.add_parser("list", help="Display all saved website data")
        show_parser.set_defaults(func=show_db)

        # Add command
        add_parser = subparsers.add_parser("add", help="Add website to configuration")
        add_parser.add_argument("-p", "--password", dest="password", action="store_true", help="Password for this application that was set during initialization")
        add_parser.add_argument("--url", required=True, help="URL of the website")
        add_parser.add_argument('-k', "--keys", nargs="+", required=True, help="List of keys for the website.")
        add_parser.add_argument("-sp", "--site_password", dest="site_password", action="store_true", help="Password for the website")
        add_parser.add_argument("-su", "--site_username", dest="site_username", action="store_true", help="Password for the website")
        add_parser.set_defaults(func=add)

        # Visit command
        visit_parser = subparsers.add_parser("visit", help="Visit an existing website by its key.")
        visit_parser.add_argument('-k', "--site_key", required=True, help="Website key")
        visit_parser.set_defaults(func=visit)

        # Search command
        search_parser = subparsers.add_parser("search", help="Search an existing website by its key.")
        search_parser.add_argument('-k', "--site_key", required=True, help="Website key")
        search_parser.set_defaults(func=search)

        # Update command
        update_parser = subparsers.add_parser("update", help="Update an existing website data.")
        update_parser.add_argument("-p", "--password", dest="password", action="store_true", help="Password for this application that was set during initialization")
        update_parser.add_argument("--url", required=True, help="URL of the website to update")
        update_parser.add_argument('-k', "--keys", nargs="+", default=None, help="List of keys for the website.")
        update_parser.add_argument("-sp", "--site_password", dest="site_password", action="store_true", help="Password for the website")
        update_parser.add_argument("-su", "--site_username", dest="site_username", action="store_true", help="Password for the website")
        update_parser.set_defaults(func=update)

        # Delete command
        del_parser = subparsers.add_parser("del", help="Delete an existing website by its key.")
        del_parser.add_argument('-k', "--site_key", required=True, help="Website key")
        del_parser.set_defaults(func=delete_site)

    # Help command
    help_parser = subparsers.add_parser("help", help="Help command")
    help_parser.set_defaults(func=help)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
