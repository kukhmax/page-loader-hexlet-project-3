#!usr/bin/env python3

import os
import re
import requests
from page_loader.parser_images import download_images

PWD = os.getcwd()


def download(url, path_to_dir):
    path_to_html = download_html(url, path_to_dir)
    return download_images(url, path_to_html)


def download_html(url: str, path_to_dir: str = PWD) -> str:
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
