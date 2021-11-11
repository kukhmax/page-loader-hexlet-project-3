#!usr/bin/env python3

import os
import requests
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Any, List, Tuple
import logging
from progress.spinner import Spinner


logger_pars = logging.getLogger('app_logger.pars')

SRC, IMG, SCRIPT, HREF, LINK = 'src', 'img', 'script', 'href', 'link'


class MySpinner(Spinner):
    phases = ['✓ ']


class AppFileError(OSError):
    pass


def download_resources(url: str, soup: Any, dir: str) -> Any:
    """Downloads scripts and links from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            soup(Any): content of html file
            dir(str): path to directory where local resources are saved

        Retruns:
            path_to_html(str): path to the modified html file
    """
    list_of_links, list_of_tags = get_links_and_tags(soup, url)
    spinner = MySpinner(' ')
    state = 'go'
    while state != 'FINISHED':
        for index, link_to_resource in enumerate(list_of_links):
            if urlparse(url).netloc != urlparse(link_to_resource).netloc:
                continue

            try:
                logger_pars.debug(f'link to download is {link_to_resource}')
                response = requests.get(link_to_resource, stream=True)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger_pars.error(e)
                continue

            file_name = make_file_name(link_to_resource)
            change_link_to_path(dir, list_of_tags, index, file_name)

            spinner.next()
            print(link_to_resource)

            write_content_of_resource_to_file(dir, file_name, response)

        state = 'FINISHED'
    return soup


def write_content_of_resource_to_file(dir, file_name, response):
    path_to_resource = os.path.join(dir, file_name)
    with open(path_to_resource, 'wb') as file:
        try:
            file.write(response.content)
        except PermissionError:
            logger_pars.error(f'PermissionError: {path_to_resource}')
            raise PermissionError(f"You don't have permission \
to {path_to_resource}")
        except OSError as e:
            logger_pars.error(f'Unknown error: {e}-{path_to_resource}')
            raise AppFileError(e) from e


def get_links_and_tags(soup: Any, url: str) -> Tuple[List[str], List[Any]]:
    """Get list of links to resources"""
    tags = {IMG: SRC, SCRIPT: SRC, LINK: HREF}
    list_of_tags = []
    list_of_links = []
    for tag_parent, tag in tags.items():
        list_of_links.extend(
            [urljoin(
                url, source.get(tags[tag_parent])
            ) for source in soup(tag_parent)]
        )
        list_of_tags.extend(
            [source for source in soup(tag_parent)]
        )
    return list_of_links, list_of_tags


def make_file_name(link_to_resource: str) -> str:
    suffix = Path(link_to_resource).suffix.lower()
    netloc = urlparse(link_to_resource).netloc
    path = urlparse(link_to_resource).path

    if not suffix:
        path += '.html'
    tmp = re.sub(r'[^a-zA-Z0-9]+', '-',
                 f'{netloc}{path}').rsplit('-', 1)
    file_name = f'{tmp[0]}.{tmp[1]}'
    return file_name


def change_link_to_path(dir, list_of_tags, index, file_name):
    work_dir = re.sub(r'[\/\-\_a-zA-Z0-9]{0,}(?=\/)\/', '', dir)

    if SCRIPT in str(list_of_tags[index]) or IMG in str(list_of_tags[index]):
        list_of_tags[index][SRC] = os.path.join(work_dir, file_name)
    elif LINK in str(list_of_tags[index]):
        list_of_tags[index][HREF] = os.path.join(work_dir, file_name)
