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


def download_resources(url: str, soup: Any, dir: str) -> Any:  # noqa C901
    """Downloads resources from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            soup(Any): content of html file
            dir(str): path to directory where local resources are saved

        Retruns:
            soup(Any): path to the modified html file
    """
    list_of_links_and_tags = get_links_and_tags(soup, url)
    spinner = MySpinner(' ')
    state = 'go'
    while state != 'FINISHED':
        for (link_to_resource, tag) in list_of_links_and_tags:
            if urlparse(url).netloc != urlparse(link_to_resource).netloc:
                continue

            if not request_link_to_resource(link_to_resource):
                continue
            else:
                response = request_link_to_resource(link_to_resource)

            file_name = make_file_name(link_to_resource)
            change_link_to_path(dir, tag, file_name)

            spinner.next()
            print(link_to_resource)

            write_content_of_resource_to_file(dir, file_name, response)

        state = 'FINISHED'
    return soup


def request_link_to_resource(link_to_resource):
    """Make a request for a link with a resource."""
    try:
        logger_pars.debug(f'link to download is {link_to_resource}')
        response = requests.get(link_to_resource, stream=True)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger_pars.error(e)
    except Exception as e:
        logger_pars.error(e)


def write_content_of_resource_to_file(dir, file_name, response):
    """Writes content from the resource to a local file."""
    path_to_resource = os.path.join(dir, file_name)
    with open(path_to_resource, 'wb') as file:
        try:
            chunks = response.iter_content(chunk_size=None)
            for chunk in chunks:
                file.write(chunk)
        except PermissionError:
            logger_pars.error(f'PermissionError: {path_to_resource}')
            raise PermissionError(f"You don't have permission to {path_to_resource}")  # noqa E501
        except OSError as e:
            logger_pars.error(f'Unknown error: {e}-{path_to_resource}')
            raise AppFileError(e) from e


def get_links_and_tags(soup: Any, url: str) -> List[Tuple[str, Any]]:
    """Get list of links to resources."""
    tags = {IMG: SRC, SCRIPT: SRC, LINK: HREF}
    list_of_links_and_tags = []
    for tag in tags.keys():
        list_of_links_and_tags.extend(
            [(urljoin(
                url, source.get(tags[tag])
            ), source) for source in soup.find_all(tag)]
        )
    return list_of_links_and_tags


def make_file_name(link_to_resource: str) -> str:
    """Make file name from link to resource."""
    suffix = Path(link_to_resource).suffix.lower()
    netloc = urlparse(link_to_resource).netloc
    path = urlparse(link_to_resource).path

    if not suffix:
        path += '.html'
    tmp = re.sub(r'[^a-zA-Z0-9]+', '-',
                 f'{netloc}{path}').rsplit('-', 1)
    file_name = f'{tmp[0]}.{tmp[1]}'
    return file_name


def change_link_to_path(dir, tag, file_name):
    """Changes link to resources."""
    work_dir = re.sub(r'[\/\-\_a-zA-Z0-9]{0,}(?=\/)\/', '', dir)

    if SRC in str(tag):
        tag[SRC] = os.path.join(work_dir, file_name)
    elif HREF in str(tag):
        tag[HREF] = os.path.join(work_dir, file_name)
