#!usr/bin/env python3

import os
import requests
from page_loader.parser_resources import download_resources
from page_loader.utilities import make_dir_and_soup, make_prettify
from page_loader.utilities import update_url_to_file_name
import logging

WD = os.getcwd()

logger_resp = logging.getLogger('app_logger.response')


class AppError(Exception):
    pass


class AppConnectionError(AppError):
    pass


def download(url, path_to_dir=WD):
    path_to_html = download_html(url, path_to_dir)
    soup, dir = make_dir_and_soup(path_to_html)
    soup = download_resources(url, soup, dir)
    return make_prettify(path_to_html, soup)


def download_html(url: str, path_to_dir: str = WD) -> str:
    """Downloads the content of the site page
       and displays the full path to the uploaded file
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except (requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema,
            requests.exceptions.InvalidURL) as e:
        logger_resp.error(e)
        raise AppError('Wrong address!') from e
    except requests.exceptions.HTTPError as e:
        logger_resp.error(e)
        raise AppError(f'Connection failed. Status code is \
{requests.get(url).status_code}') from e
    except requests.exceptions.RequestException as e:
        logger_resp.error(f'Error is {e}')
        raise requests.exceptions.RequestException(f'Error is {e}') from e

    path_to_file = update_url_to_file_name(url, path_to_dir)
    with open(path_to_file, 'w+') as f:
        f.write(resp.text)
    return path_to_file
