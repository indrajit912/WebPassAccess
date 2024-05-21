# WebPassAccess - A script that can visit various website
# Author: Indrajit Ghosh
# Created On: Sep 27, 2023
# Modified On: May 21, 2024
# 
# USAGES:
#   - python main.py add --url www.twitter.com --password <newpassword> --keys <key1> <key2>
#   - python main.py visit --site_key <key>
#   - python main.py update --url www.twitter.com --password <anotherpass> --keys <key3> <key4>
# 
import sys
import pyperclip
import webbrowser
import logging
import argparse
import json
from pathlib import Path

from mappings import create_site_mapping, create_password_mapping, add_website_to_config, sha256

BASE_DIR = Path(__name__).parent.absolute()
CONFIG_JSON = BASE_DIR / 'config.json'
DOT_ENV_FILE = BASE_DIR / '.env'

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%d-%b-%Y %I:%M:%S %p',
    filename='website_visit.log',
    level=logging.INFO
)

logger = logging.getLogger("WebPassAccess.main")

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


def take_website_input():
    url = input("Enter the url (e.g- 'https://www.facebook.com'): ")
    if not url:
        print("\nNo url given. Exiting...")
        sys.exit()
    keys = input("Enter some keys for this website (separate your keys by comma; e.g- 'fb, facebook, fbook'): ").split(', ')
    passwd = input("Do you want to add the password for this website? Leave it blank if not or else enter the password: ")
    passwd = None if passwd == '' else passwd

    return url, keys, passwd


def add(args):
    url = args.url
    keys = args.keys
    passwd = args.password

    add_website_to_config(
        filename=CONFIG_JSON,
        url=url,
        keys=keys,
        password=passwd
    )
    print("Website added successfully!")


def help(args):
    print("USAGES:")

def visit(args):
    site_mapping, config = create_site_mapping(CONFIG_JSON)
    password_mapping = create_password_mapping(DOT_ENV_FILE)
    site_key = args.site_key

    site_url_hash = site_mapping.get(site_key)
    if site_url_hash is None:
        logger.error(f"Site key '{site_key}' not found in mappings.")
        return

    site_url = config['websites'][site_url_hash]['url']
    site_passwd = password_mapping.get(site_url_hash)

    visit_site(url=site_url, passwd=site_passwd)

def update(args):
    url = args.url

    with open(CONFIG_JSON, 'r') as file:
        config = json.load(file)
    
    if not sha256(url) in config["websites"].keys():
        print(f"No website with the url '{url}' found! Exiting ...")
        sys.exit()

    keys = (
        args.keys
        if args.keys
        else config["websites"][sha256(url)]["keys"]
    )
    passwd = args.password

    add_website_to_config(
        filename=CONFIG_JSON,
        url=url,
        keys=keys,
        password=passwd
    )
    print("Website updated successfully!")

def main():
    parser = argparse.ArgumentParser(description="CLI Application")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add website to configuration")
    add_parser.add_argument("--url", required=True, help="URL of the website")
    add_parser.add_argument("--keys", nargs="+", required=True, help="List of keys for the website.")
    add_parser.add_argument("--password", default=None, help="Password for the website (Optional)")
    add_parser.set_defaults(func=add)

    visit_parser = subparsers.add_parser("visit", help="Visit an existing website by its key.")
    visit_parser.add_argument("--site_key", required=True, help="Website key")
    visit_parser.set_defaults(func=visit)

    update_parser = subparsers.add_parser("update", help="Update an existing website data.")
    update_parser.add_argument("--url", required=True, help="URL of the website to update")
    update_parser.add_argument("--keys", nargs="+", default=None, help="List of keys for the website.")
    update_parser.add_argument("--password", default=None, help="Password for the website")
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
