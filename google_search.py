#! usr/bin/python3
# google.py - Launches a Google search in the browser using a keyword from
# command line

import sys
import webbrowser

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Get the address from the command line
        address = ' '.join(sys.argv[1:])
        webbrowser.open('https://www.google.com/search?q=' + address)

    else:
        # Open Google search
        webbrowser.open('https://www.google.com/search?q=')

    