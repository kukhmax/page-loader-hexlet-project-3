#!usr/bin/env python3

import os
import re
import logging
import requests
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from page_loader.parser_resources import download_resources

WD = os.getcwd()

logger_resp = logging.getLogger('app_logger.response')


class AppError(Exception):
    pass


def download(url, path_to_dir=WD):
    path_to_html = download_html(url, path_to_dir)
    dir_name = Path(path_to_html).stem + '_files'
    full_path_to_dir = make_dir_to_save_files(path_to_html)
    soup = make_soup(path_to_html)
    soup_with_path_to_resources = download_resources(url, soup,
                                                     full_path_to_dir, dir_name)
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

    file_name = create_file_name_from_url(url)
    full_path_to_file = os.path.join(path_to_dir, file_name)
    try:
        with open(full_path_to_file, 'w+') as f:
            f.write(resp.text)
    except PermissionError:
        logger_resp.error(f'PermissionError: {full_path_to_file}')
        raise PermissionError(f"You don't have permission: '{full_path_to_file}'")  # noqa E501
    except OSError as err:
        logger_resp.error(f'Unknown error: {err}')
        raise AppError(f'Unknown error: {err}') from err
    return full_path_to_file


def create_file_name_from_url(url: str) -> str:
    """Collects the full path to the file."""
    def make_format(url):
        return '{}.html'.format(re.sub(r'\W', '-', url))
    url_without_scheme = '{}{}'.format(urlparse(url).netloc,
                                       urlparse(url).path)
    url_without_suffix = '{}/{}'.format(Path(url_without_scheme).parent,
                                        Path(url_without_scheme).stem)
    if Path(url).suffix == '.html':
        return make_format(url_without_suffix)
    return make_format(url_without_scheme)


def make_prettify(path_to_html: str, soup: Any) -> str:
    """Modifies the parse tree into a nicely formatted Unicode string,
       where each tag and each line is output on a separate line

       Agrs:
            path_to_html(str): path to html file
            soup(Any): object, which represents the document
                  as a nested data structure

       Returns:
            path to modified html file
    """
    try:
        with open(path_to_html, 'w+') as update_file:
            content = soup.prettify()
            update_file.write(content)
    except PermissionError:
        logger_resp.error(f'PermissionError: {path_to_html}')
        raise PermissionError(f"You don't have permission: '{path_to_html}'")  # noqa E501
    except OSError as err:
        logger_resp.error(f'Unknown error: {err}')
        raise AppError(f'Unknown error: {err}') from err

    return path_to_html


def make_dir_to_save_files(path_to_html: str) -> str:
    """Makes directory to save files from html page

       Args:
            path_to_html(str): path to html file

       Returns:
            dir: path to directory
    """
    dir = '{}/{}_files'.format(Path(path_to_html).parent,
                               Path(path_to_html).stem)
    try:
        os.mkdir(dir)
    except FileExistsError as e:
        logger_resp.error(e)
        raise AppError(f"directory '{dir}' is exists") from e
    except OSError as e:
        logger_resp.error(f"Can't create directory. {e}")
        raise AppError(f"Can't create directory. {e}") from e
    return dir


def make_soup(path_to_html: str) -> str:
    """Makes object, which represents
       the document as a nested data structure

        Args:
            path_to_html(str): path to html file

        Retruns:
            soup: object, which represents the document
                  as a nested data structure
    """
    try:
        with open(path_to_html) as f:
            return BeautifulSoup(f, 'html.parser')
    except PermissionError:
        logger_resp.error(f'PermissionError: {path_to_html}')
        raise PermissionError(f"You don't have permission: '{path_to_html}'")  # noqa E501
    except OSError as err:
        logger_resp.error(f'Unknown error: {err}')
        raise AppError(f'Unknown error: {err}') from err
