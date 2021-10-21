#!usr/bin/env python3

import os
import requests
import re

PWD = os.getcwd()


def get_response(url):
    return requests.get(url)


def download(url: str, path_to_dir: str = PWD) -> str:
    """Downloads the content of the site page
       and displays the full path to the uploaded file
    """
    response = requests.get(url)
    path_to_file = update_url_to_file_name(url, path_to_dir)
    with open(path_to_file, 'w+') as f:
        f.write(response.text)
    return path_to_file


def update_url_to_file_name(url: str, path_to_dir: str) -> str:
    """Collects the full path to the file"""
    update_url = re.sub(r'$', '.html',
                        re.sub(r'\W', '-',
                               re.sub(r'^htt(ps|p)://', '', url)))
    return os.path.join(path_to_dir, update_url)

# download('https://python-scripts.com/beautifulsoup-html-parsing', PWD)