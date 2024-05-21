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

def sha256(text:str):
    return hashlib.sha256(text.encode()).hexdigest()


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

    url_hash = sha256(url)

    add_password = True

    if url_hash in config['websites']:
        if password:
            # Remove existing password line from .env
            existing_url = config['websites'][url_hash]['url']
            existing_url_hash = sha256(existing_url)

            with open(dotenv_path, 'r') as env_file:
                lines = env_file.readlines()

            with open(dotenv_path, 'w') as env_file:
                # Writing rest of the lines except for the url given
                for line in lines:
                    if not line.startswith(existing_url_hash):
                        env_file.write(line)
        else:
            add_password = False

        # Append keys to existing entry
        config['websites'][url_hash]['keys'].extend(keys)
        config['websites'][url_hash]['keys'] = list(set(config['websites'][url_hash]['keys']))
    else:
        config['websites'][url_hash] = {'keys': keys, 'url': url}

    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)

    if password and add_password:
        hashed_password = sha256(url)
        with open(dotenv_path, 'a') as env_file:
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
        config = {}
        site_mapping = {}
        return site_mapping, config

    site_mapping = {}
    for url_hash, website_info in config.get('websites', {}).items():
        for key in website_info['keys']:
            site_mapping[key] = url_hash

    return site_mapping, config


def create_password_mapping(dot_env_file):
    """
    Create a password_mapping dictionary from the .env file.

    Returns:
        dict: A dictionary mapping SHA256 hashes of website URLs to their passwords.
    """
    password_mapping = {}

    with open(dot_env_file, 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line:
                url_hash, password = line.split('=')
                password_mapping[url_hash] = password

    return password_mapping