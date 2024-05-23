# WebPassAccess

WebPassAccess is a Python script designed to manage website access and passwords securely. It allows users to store website URLs, associated keys, usernames, and passwords in an encrypted configuration file. The script can then open websites in a web browser and copy passwords to the clipboard for easy access.

## Author
- [Indrajit Ghosh](https://github.com/indrajit912)


## Features

- Securely store website URLs, keys, usernames, and passwords.
- Encrypt sensitive information using cryptography.
- Open websites in a web browser with a single command.
- Copy passwords to the clipboard for convenience.

## Prerequisites

- Python 3.x
- `pip` package manager
- Dependencies listed in `requirements.txt`


## WebPassAccess Command Documentation

### `init`
Initialize the application by creating necessary data structures and encryption keys.

Usage:
```bash
python3 main.py init
```


### `db`
Display all saved website data.

Usage:

```bash
python3 main.py db
```


### `add`
Add a website to the database.

Options:
- `-p`, `--password`: Password for the application set during initialization.
- `--url`: URL of the website.
- `-k`, `--keys`: List of keys for the website.
- `-sp`, `--site_password`: Flag to include password for the website.
- `-su`, `--site_username`: Flag to include username for the website.

Usage:
```bash
python3 main.py add [-p] --url <URL> -k <KEYS> [-sp] [-su]
```


### `visit`
Visit an existing website by its key.

Options:
- `-k`, `--site_key`: Website key.

Usage:
```bash
python3 main.py visit -k <SITE_KEY>
```


### `update`
Update an existing website data.

Options:
- `-p`, `--password`: Password for the application set during initialization.
- `--url`: URL of the website to update.
- `-k`, `--keys`: List of keys for the website.
- `-sp`, `--site_password`: Flag to include password for the website.
- `-su`, `--site_username`: Flag to include username for the website.

Usage:
```bash
python3 main.py update [-p] --url <URL> [-k <KEYS>] [-sp] [-su]
```


### `help`
Show help message.

Usage:
```bash
python3 main.py help
```

For more information on a specific command, use ```python3 main.py [command] --help```.



## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

