# WebPassAccess
WebPassAccess is a Python script that allows you to easily access various websites by providing a site key, which corresponds to the URL and password associated with that website. It automates the process of copying the password to the clipboard and opening the website in a web browser.

## Author
- [Indrajit Ghosh](https://github.com/indrajit912)

## Features
- Access websites quickly by providing a site key.
- Copies the associated password to the clipboard for easy login.

## Usage
To use WebPassAccess, follow these steps:

1. Open websites.py and add your website URL as a Python variable. For example, if you want to access Facebook, add the following line:
```bash
FB_LOGIN_PAGE = "https://www.facebook.com/"
```
2. (Optional) If you want to add a password for the website, create (if not exists) a .env file and add your website's password. For example:
```python
FACEBOOK_PASSWD=my-fb-passwd-here
```
3. Open the mappings.py file and add a suitable key for your website in the SITE_MAPPING dictionary. If you have saved the password in .env, add that in the SITE_PASSWD_MAPPING dictionary. For example, for Facebook:
```python
SITE_MAPPING = {
    "fb": FB_LOGIN_PAGE
}

SITE_PASSWD_MAPPING ={
    FB_LOGIN_PAGE: os.environ.get("FACEBOOK_PASSWD")
}
```
4. From the next time onward, just run the script with the appropriate site key. For example:
```bash
python main.py fb
```
This will open the corresponding website in your default web browser and copy the associated password to the clipboard for easy login.

## TODO
- Use a `sqlite` database to store the passwords.
- Encrypt the passwords and then store it.
- Build a robust cli to let user add their site url, password and keys.

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

