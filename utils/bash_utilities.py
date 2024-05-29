# Bashrc utility file for webpassaccess!
# Author: Indrajit Ghosh
# Created On: May 23, 2024
# 

import os
import sys
from pathlib import Path
import subprocess


def source_bashrc():
    """
    Sources the .bashrc file to apply the changes to the current shell session.
    """
    bashrc_path = Path.home() / '.bashrc'
    if bashrc_path.exists():
        subprocess.run(["bash", "-c", f"source {bashrc_path}"])


def generate_alias(alias_name, commands):
    """
    Generates an alias string for a given alias name and list of commands.

    Args:
        alias_name (str): The name of the alias.
        commands (list): List of commands to be aliased.

    Returns:
        str: The alias string.
    """
    alias_str = "alias {}='{}'".format(alias_name, " ".join(commands))
    return alias_str


def replace_alias(alias_name, new_content):
    """
    Replaces the content of an existing alias after the '=' sign in the .bashrc file.

    Args:
        alias_name (str): The name of the alias to be replaced.
        new_content (str): The new content to replace the existing content.

    Raises:
        OSError: If the operating system is Windows.
        ValueError: If the alias name doesn't exist in the .bashrc file.
    """
    if os.name == 'posix':
        # Determine the user's home directory
        home_dir = os.path.expanduser("~")
        bashrc_path = os.path.join(home_dir, '.bashrc')

        # Check if .bashrc exists
        if not os.path.exists(bashrc_path):
            raise OSError("No .bashrc file found.")

        # Read the content of .bashrc
        with open(bashrc_path, 'r') as f:
            lines = f.readlines()

        # Find and replace the alias content
        replaced = False
        for i, line in enumerate(lines):
            if line.startswith('alias {}='.format(alias_name)):
                lines[i] = 'alias {}={}\n'.format(alias_name, new_content)
                replaced = True
                break

        if not replaced:
            raise ValueError("Alias '{}' not found in .bashrc file.".format(alias_name))

        # Write the modified content back to .bashrc
        with open(bashrc_path, 'w') as f:
            f.writelines(lines)

        print("Alias '{}' content replaced in .bashrc.".format(alias_name))

    elif os.name == 'nt':
        raise OSError("Windows is not supported. Only Linux and macOS are supported.")


def alias_string_in_bashrc(alias_string:str, bashrc_path:str=Path.home() / '.bashrc'):
    """Returns True if the alias_name is present in `.bashrc`, otherwise a False"""
    # Check if alias name already exists in .bashrc
    with open(bashrc_path, 'r') as f:
        existing_aliases = f.read()
        if alias_string.split('=')[0] in existing_aliases:
            return True
    return False


def add_alias_to_bash_profile(alias_string: str, replace: bool = False):
    """
    Adds an alias string to the user's .bashrc file.

    Args:
        alias_string (str): The alias string to be added.
        replace (bool): If True, replaces the existing alias if found. Default is False.

    Raises:
        OSError: If the operating system is Windows.
        ValueError: If the alias name already exists in the .bashrc file and replace is False.
    """
    if os.name == 'posix':
        # Determine the user's home directory
        home_dir = os.path.expanduser("~")
        bashrc_path = os.path.join(home_dir, '.bashrc')

        # Check if .bashrc exists, if not create it
        if not os.path.exists(bashrc_path):
            open(bashrc_path, 'a').close()


        if alias_string_in_bashrc(alias_string, bashrc_path):
            if not replace:
                raise ValueError("Alias name already exists in .bashrc file.")
            else:
                alias_name, new_content = alias_string.split('=')
                replace_alias(alias_name=alias_name.lstrip('alias '), new_content=new_content)
        else:
            # Append alias string to the .bashrc file
            with open(bashrc_path, 'a') as profile:
                profile.write('\n' + alias_string + '\n')
            print("Alias added to .bashrc.")

    elif os.name == 'nt':
        raise OSError("Windows is not supported. Only Linux and macOS are supported.")


def add_wpa_command_aliases_to_bashrc(main_script_path:Path=Path.cwd() / 'main.py'):
    """Returns a list of alias strings that to be added to the bash profile"""
    if not main_script_path.exists():
        print(f"File not found: '{main_script_path}'")
        return
    
    wpa_aliases = {
        "add": "wpa-add",
        "update": "wpa-update",
        "visit": "visit",
        "list": "wpa-list",
        "del": "wpa-del",
        "search": "wpa-search"
    }
    
    add_alias = generate_alias(
        alias_name=wpa_aliases['add'],
        commands=[sys.executable, str(main_script_path), "add", "-p", "--url"]
    )
    add_alias_to_bash_profile(alias_string=add_alias, replace=True)

    update_alias = generate_alias(
        alias_name=wpa_aliases['update'],
        commands=[sys.executable, str(main_script_path), "update", "-p", "--url"]
    )
    add_alias_to_bash_profile(alias_string=update_alias, replace=True)

    visit_alias = generate_alias(
        alias_name=wpa_aliases['visit'],
        commands=[sys.executable, str(main_script_path), "visit", "-k"]
    )
    add_alias_to_bash_profile(alias_string=visit_alias, replace=True)

    search_alias = generate_alias(
        alias_name=wpa_aliases['search'],
        commands=[sys.executable, str(main_script_path), "search", "-k"]
    )
    add_alias_to_bash_profile(alias_string=search_alias, replace=True)

    db_alias = generate_alias(
        alias_name=wpa_aliases['list'],
        commands=[sys.executable, str(main_script_path), "list"]
    )
    add_alias_to_bash_profile(alias_string=db_alias, replace=True)

    del_alias = generate_alias(
        alias_name=wpa_aliases['del'],
        commands=[sys.executable, str(main_script_path), "del", "-k"]
    )
    add_alias_to_bash_profile(alias_string=del_alias, replace=True)

    # Source the .bashrc
    source_bashrc()
