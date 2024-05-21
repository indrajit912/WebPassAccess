"""
Author: Indrajit Ghosh
Created On: Sep 27, 2023

This script loads environment variables from a .env file using the dotenv library.
It retrieves the value of a specific environment variable, YOUR_VAR_SAVED_IN_DOT_ENV,
and assigns it to the variable YOUR_VAR_SAVED_IN_DOT_ENV.

Make sure to customize the environment variable name ("YOUR_VAR_SAVED_IN_DOT_ENV")
based on your actual use case.
"""

import os
from os.path import join, dirname
from dotenv import load_dotenv
import json
import hashlib
from websites import *

# Define the path to the .env file
dotenv_path = join(dirname(__file__), '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)


SITE_MAPPING = {
    "gpt":  CHATGPT_LOGIN_URL,
    "chatgpt": CHATGPT_LOGIN_URL,
    "isimail": ISIBC_OUTLOOK_MAIL_URL,
    "gmail": GMAIL_URL,
    "mail": GMAIL_URL,
    "overleaf": OVERLEAF_URL,
    "screener": SCREENER_URL,
    "github": GITHUB_LOGIN_PAGE,
    "fb": FB_LOGIN_PAGE,
    "facebook": FB_LOGIN_PAGE,
    "dropbox": DROPBOX_HOME_URL,
    "drive": GOOGLE_DRIVE_URL,
    "gdrive": GOOGLE_DRIVE_URL,
    "googledrive": GOOGLE_DRIVE_URL,
    "gdoc": GOOGLE_DOC_URL,
    "doc": GOOGLE_DOC_URL,
    "googledoc": GOOGLE_DOC_URL,
    "statmath": STATMATH_ISIBANG_PAGE,
    "isibang": ISIBANG_WEBSITE
}

SITE_PASSWD_MAPPING = {
    CHATGPT_LOGIN_URL: os.environ.get("OPEN_AI_PASSWD"),
    ISIBC_OUTLOOK_MAIL_URL: os.environ.get("ISI_MAIL_PASSWD"),
    GITHUB_LOGIN_PAGE: os.environ.get('GITHUB_PASSWD'),
    OVERLEAF_URL: os.environ.get("OVERLEAF_PASSWD"),
    SCREENER_URL: os.environ.get("SCREENER_PASSWD")
}

def add_website_to_config(filename, url, keys, password=None):
    """
    Add a new website entry to the config.json file.

    Args:
        filename (str): The filename of the config.json file.
        url (str): The URL of the website to add.
        keys (list): A list of keys associated with the website.
        password (str, optional): The password associated with the website. Defaults to None.

    Returns:
        None
    """
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {'websites': {}}

    url_hash = hashlib.sha256(url.encode()).hexdigest()
    add_password = True

    if url_hash in config['websites']:
        if password:
            # Remove existing password line from .env
            existing_url = config['websites'][url_hash]['url']
            existing_url_hash = hashlib.sha256(existing_url.encode()).hexdigest()
            with open('.env', 'r') as env_file:
                lines = env_file.readlines()
            with open('.env', 'w') as env_file:
                for line in lines:
                    if not line.startswith(existing_url_hash):
                        env_file.write(line)

            add_password = False
        # Append keys to existing entry
        config['websites'][url_hash]['keys'].extend(keys)
    else:
        config['websites'][url_hash] = {'keys': keys, 'url': url}

    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)

    if password and add_password:
        hashed_password = hashlib.sha256(url.encode()).hexdigest()
        with open('.env', 'a') as env_file:
            env_file.write(f"{hashed_password}={password}\n")

def create_site_mapping(filename):
    """
    Create a site_mapping dictionary based on the URLs in the config.json file.

    Args:
        filename (str): The filename of the config.json file.

    Returns:
        dict: A dictionary mapping site keys to SHA256 hashes of website URLs.
    """
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        return {}

    site_mapping = {}
    for url_hash, website_info in config.get('websites', {}).items():
        for key in website_info['keys']:
            site_mapping[key] = url_hash

    return site_mapping, config


def create_password_mapping():
    """
    Create a password_mapping dictionary from the .env file.

    Returns:
        dict: A dictionary mapping SHA256 hashes of website URLs to their passwords.
    """
    password_mapping = {}

    with open('.env', 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line:
                url_hash, password = line.split('=')
                password_mapping[url_hash] = password

    return password_mapping