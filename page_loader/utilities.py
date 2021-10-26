#!usr/bin/env python3

import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from typing import Any, Tuple
import logging
import shutil

logger_util = logging.getLogger('app_logger.util')


def make_dir_and_soup(path_to_html: str) -> Tuple[Any, str]:
    """Makes directory and retruns object,
       which represents the document as a nested data structure

       Args:
            path_to_html(str): path to html file

       Returns:
            soup: object, which represents the document
                  as a nested data structure
             dir: path to directory
    """
    with open(path_to_html) as f:
        dir = re.sub('.html$', '_files', path_to_html)
        try:
            os.mkdir(dir)
        except FileExistsError:
            logger_util.exception(f"dirrectory '{dir}' is exists")
            shutil.rmtree(dir)
            os.mkdir(dir)
        soup = BeautifulSoup(f, 'html.parser')
    return soup, dir


def get_resourсe_url(url: str, src: str) -> Any:
    """Creates a link to download resourсу"""
    domain = urlparse(url).netloc
    src_netloc = urlparse(src).netloc
    path = urlparse(src).path
    scheme = urlparse(src).scheme
    if src_netloc == domain:
        if scheme == '':
            scheme = 'https'
            return urlunparse((scheme, domain, path, '', '', ''))
        else:
            return src
    elif src_netloc == '':
        scheme = 'https'
        return urlunparse((scheme, domain, path, '', '', ''))
    else:
        return None


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
