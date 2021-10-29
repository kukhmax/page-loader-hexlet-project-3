#!usr/bin/env python3

import os
import requests
from page_loader.parser_resources import download_resources
from page_loader.utilities import make_dir_and_soup, make_prettify
from page_loader.utilities import update_url_to_file_name
import logging

logger_resp = logging.getLogger('app_logger.response')

WD = os.getcwd()


def download(url, path_to_dir=WD):
    path_to_html = download_html(url, path_to_dir)
    soup, dir = make_dir_and_soup(path_to_html)
    soup = download_resources(url, soup, dir)
    print(f"\x1b[3m\x1b[32mPage was successfuly \
downloaded into '{path_to_html}'\x1b[0m\x1b[37m")
    return make_prettify(path_to_html, soup)


def download_html(url: str, path_to_dir: str = WD) -> str:
    """Downloads the content of the site page
       and displays the full path to the uploaded file
    """
    try:
        resp = requests.get(url)
    except IOError:
        logger_resp.error(f'HTTP status codes reference \
{requests.get(url).status_code} :: URL: {url}')
        raise requests.HTTPError(f'response {requests.get(url).status_code}')
    path_to_file = update_url_to_file_name(url, path_to_dir)
    with open(path_to_file, 'w+') as f:
        f.write(resp.text)
    return path_to_file
