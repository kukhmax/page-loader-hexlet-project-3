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
    links_and_tags_of_resourses = get_links_and_tags_of_resources(soup, url)
    spinner = MySpinner(' ')
    for (link_to_resource, tag) in links_and_tags_of_resourses:
        if not is_local_resource(url, link_to_resource):
            continue

        try:
            response = request_link_to_resource(link_to_resource)
        except requests.exceptions.RequestException as e:
            logger_pars.error(e)
            continue

        file_name = make_file_name(link_to_resource)
        change_link_to_file_path(dir, tag, file_name)

        spinner.next()
        print(link_to_resource)

        write_content_of_resource_to_file(dir, file_name, response)

    return soup


def is_local_resource(url: str, link_to_resource: str) -> bool:
    if urlparse(url).netloc != urlparse(link_to_resource).netloc:
        return False
    return True


def request_link_to_resource(link_to_resource):
    """Make a request for a link with a resource."""
    logger_pars.debug(f'link to download is {link_to_resource}')
    response = requests.get(link_to_resource, stream=True)
    response.raise_for_status()
    return response


def write_content_of_resource_to_file(dir, file_name, response):
    """Writes content from the resource to a local file."""
    path_to_resource = os.path.join(dir, file_name)
    try:
        with open(path_to_resource, 'wb') as file:
            chunks = response.iter_content(chunk_size=None)
            for chunk in chunks:
                file.write(chunk)
    except PermissionError:
        logger_pars.error(f'PermissionError: {path_to_resource}')
        raise PermissionError(f"You don't have permission to {path_to_resource}")  # noqa E501
    except OSError as e:
        logger_pars.error(f'Unknown error: {e}-{path_to_resource}')
        raise AppFileError(e) from e


def get_links_and_tags_of_resources(soup: Any,
                                    url: str) -> List[Tuple[str, Any]]:
    """Get list of links to resources."""
    tags = {IMG: SRC, SCRIPT: SRC, LINK: HREF}
    links_and_tags_of_resourses = []
    for tag in tags:
        links_and_tags_of_resourses.extend(
            [(urljoin(
                url, source.get(tags[tag])
            ), source) for source in soup.find_all(tag) if tags[tag]]
        )
    return links_and_tags_of_resourses


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


def change_link_to_file_path(dir, tag, file_name):
    """Changes link to resources."""
    work_dir = re.sub(r'[\/\-\_a-zA-Z0-9]{0,}(?=\/)\/', '', dir)

    if IMG in str(tag) or SCRIPT in str(tag):
        if HREF not in str(tag):
            tag[SRC] = os.path.join(work_dir, file_name)
    if LINK in str(tag):
        tag[HREF] = os.path.join(work_dir, file_name)
