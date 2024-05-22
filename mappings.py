"""
Author: Indrajit Ghosh
Created On: Sep 27, 2023

This script loads environment variables from a .env file using the dotenv library.
It retrieves the value of a specific environment variable, YOUR_VAR_SAVED_IN_DOT_ENV,
and assigns it to the variable YOUR_VAR_SAVED_IN_DOT_ENV.

Make sure to customize the environment variable name ("YOUR_VAR_SAVED_IN_DOT_ENV")
based on your actual use case.
"""

import json

from utils.authentication import sha256
from utils.encryption import decrypt
from config import WEBSITES_DATA_JSON

def get_user_data():
    with open(WEBSITES_DATA_JSON, 'r') as file:
        user_data = json.load(file)
    return user_data

def save_user_data(data):
    with open(WEBSITES_DATA_JSON, 'w') as f:
        json.dump(data, f, indent=4)

def add_website_to_database(url, keys, password=None, username=None):
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
    user_data = get_user_data()
    url_hash = sha256(url)

    if url_hash in user_data['websites']:
        user_data['websites'][url_hash]['keys'].extend(keys)
        user_data['websites'][url_hash]['keys'] = list(set(user_data['websites'][url_hash]['keys']))
        if password:
            user_data['websites'][url_hash]['password'] = password
        if username:
            user_data['websites'][url_hash]['username'] = username

    else:
        _new_site = {
            'url': url,
            'keys': keys
        }
        if password:
            _new_site['password'] = password
        if username:
            _new_site['username'] = username

        user_data['websites'][url_hash] = _new_site

    save_user_data(user_data)


def create_site_mapping():
    """
    Create a site_mapping dictionary based on the URLs in the config.json file.

    Args:
        filename (str): The filename of the config.json file.

    Returns:
        dict: A dictionary mapping site keys to SHA256 hashes of website URLs.
    """
    user_data = get_user_data()

    site_mapping = {}
    for url_hash, website_info in user_data.get('websites', {}).items():
        for key in website_info['keys']:
            site_mapping[key] = url_hash

    return site_mapping, user_data


def create_password_mapping(app_key, user_data):
    """
    Create a password_mapping dictionary from the .env file.

    Returns:
        dict: A dictionary mapping SHA256 hashes of website URLs to their passwords.
    """
    password_mapping = {}
    for url_hash, website_info in user_data.get('websites', {}).items():
        encrypted_passwd = website_info['password']
        password = decrypt(encrypted_data=encrypted_passwd, key=app_key)
        password_mapping[url_hash] = password

    return password_mapping