#!usr/bin/env python3

import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from typing import Any, Tuple


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
