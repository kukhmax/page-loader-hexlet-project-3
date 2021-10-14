#!usr/bin/env python3

import os
import requests
import re

CWD = os.getcwd()


def download(url: str, path_to_dir: str = CWD) -> str:
    """Downloads the content of the site page
       and displays the full path to the uploaded file
    """
    r = requests.get(url)
    path_to_file = update_url_to_file_path(url, path_to_dir)
    with open(path_to_file, 'w+') as f:
        f.write(r.text)
    return path_to_file


def update_url_to_file_path(url: str, path_to_dir: str) -> str:
    """Collects the full path to the file"""
    update_url = re.sub(r'$', '.html',
                        re.sub(r'\W', '-',
                               re.sub(r'^htt(ps|p)://', '', url)))
    return os.path.join(path_to_dir, update_url)
