#!usr/bin/env python3

import os
import re
import requests
from page_loader.parser_images import download_images
from page_loader.parser_scripts import download_scripts
from page_loader.utilities import make_dir_and_soup


WD = os.getcwd()


def download(url, path_to_dir=WD):
    path_to_html = download_html(url, path_to_dir)
    soup, dir = make_dir_and_soup(path_to_html)
    soup = download_images(url, path_to_html, soup, dir)
    soup = download_scripts(url, path_to_html, soup, dir)
    return make_prettify(path_to_html, soup)


def download_html(url: str, path_to_dir: str = WD) -> str:
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


def make_prettify(path_to_html, soup):
    """Modifies the parse tree into a nicely formatted Unicode string,
       where each tag and each line is output on a separate line

       Agrs:
            path_to_html(str): path to html file
            soup(str): content of html file

       Returns:
            path to modified html file
    """
    with open(path_to_html, 'w+') as update_file:
        content = soup.prettify()
        update_file.write(re.sub(r'\/>', '>', content))
    return path_to_html
