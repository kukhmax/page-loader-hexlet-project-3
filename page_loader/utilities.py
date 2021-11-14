#!usr/bin/env python3

import os
import re
from bs4 import BeautifulSoup
from typing import Any
from pathlib import Path
import logging

logger_util = logging.getLogger('app_logger.util')


class AppError(Exception):
    pass


def make_dir_to_save_files(path_to_html: str) -> str:
    """Makes directory to save files from html page

       Args:
            path_to_html(str): path to html file

       Returns:
            dir: path to directory
    """
    dir = re.sub(r'.html$', '_files', path_to_html)
    try:
        os.mkdir(dir)
    except FileExistsError as e:
        logger_util.error(e)
        raise AppError(f"directory '{dir}' is exists") from e
    except OSError as e:
        logger_util.error(f"Can't create directory. {e}")
        raise AppError(f"Can't create directory. {e}") from e
    return dir


def make_soup(path_to_html: str) -> Any:
    """Makes object, which represents
       the document as a nested data structure

        Args:
            path_to_html(str): path to html file

        Retruns:
            soup: object, which represents the document
                  as a nested data structure
    """
    with open(path_to_html) as f:
        return BeautifulSoup(f, 'html.parser')


def update_url_to_file_name(url: str, path_to_dir: str) -> str:
    """Collects the full path to the

        Args:
            url(str): url
            path_to_dir(str): path to directory

        Returns:
            absolute path to file
    """
    if Path(url).suffix == '.html':
        update_url = re.sub(r'-html$', '.html',
                            re.sub(r'\W', '-',
                                   re.sub(r'^htt(ps|p)://', '', url)))
    else:
        update_url = re.sub(r'$', '.html',
                            re.sub(r'\W', '-',
                                   re.sub(r'^htt(ps|p)://', '', url)))
    return os.path.join(path_to_dir, update_url)


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
    with open(path_to_html, 'w+') as update_file:
        content = soup.prettify()
        update_file.write(content)
    return path_to_html
