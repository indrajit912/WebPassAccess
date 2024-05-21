# WebPassAccess - A script that can visit various website
# Author: Indrajit Ghosh
# Created On: Sep 27, 2023
# Modified On: May 21, 2024
# 
import sys
import pyperclip
import webbrowser
import logging
from pathlib import Path

from mappings import create_site_mapping, create_password_mapping

BASE_DIR = Path(__name__).parent.absolute()

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

def main(site_key=None):
    """
    Main function to visit a website specified by `site_key`.

    If `site_key` is not provided, it can be taken from command-line arguments or user input.

    Args:
        site_key (str, optional): The key associated with the website. Defaults to None.

    Returns:
        None
    """
    site_mapping, config = create_site_mapping('config.json')
    password_mapping = create_password_mapping()

    if site_key is None:
        if len(sys.argv) < 2:
            site_key = input("Enter the website key: ")
        else:
            site_key = sys.argv[1]

    site_url_hash = site_mapping.get(site_key)
    if site_url_hash is None:
        logger.error(f"Site key '{site_key}' not found in mappings.")
        return

    site_url = config['websites'][site_url_hash]['url']
    site_passwd = password_mapping.get(site_url_hash)

    visit_site(url=site_url, passwd=site_passwd)

if __name__ == '__main__':
    main()
