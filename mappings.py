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