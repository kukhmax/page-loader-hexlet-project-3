#!usr/bin/env python3

import os
import requests
from page_loader.parser_resources import download_resources
from page_loader.utilities import make_dir_to_save_files, make_prettify
from page_loader.utilities import update_url_to_file_name, make_soup, AppError
import logging

WD = os.getcwd()

logger_resp = logging.getLogger('app_logger.response')


def download(url, path_to_dir=WD):
    path_to_html = download_html(url, path_to_dir)
    dir = make_dir_to_save_files(path_to_html)
    soup = make_soup(path_to_html)
    soup_with_path_to_resources = download_resources(url, soup, dir)
    return make_prettify(path_to_html, soup_with_path_to_resources)


def download_html(url: str, path_to_dir: str = WD) -> str:
    """Downloads the content of the site page
       and displays the full path to the uploaded file
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger_resp.error(e)
        raise AppError(f'Error is {e}. Status code is \
{requests.get(url).status_code}') from e

    path_to_file = update_url_to_file_name(url, path_to_dir)
    try:
        with open(path_to_file, 'w+') as f:
            f.write(resp.text)
    except PermissionError:
        logger_resp.error(f'PermissionError: {path_to_file}')
        raise PermissionError(f"You don't have permission: \
'{path_to_file}'")
    except AppError as err:
        logger_resp.error(f'Unknown error: {err}')
        raise AppError(f'Unknown error: {err}') from err
    return path_to_file
