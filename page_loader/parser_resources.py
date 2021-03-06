#!usr/bin/env python3

import os
import re
import logging
import requests
from pathlib import Path
from colorama import Fore
from typing import Any, List, Tuple
from progress.spinner import Spinner
from urllib.parse import urlparse, urljoin


logger_pars = logging.getLogger('app_logger.pars')

SRC, IMG, SCRIPT, HREF, LINK = 'src', 'img', 'script', 'href', 'link'


class MySpinner(Spinner):
    phases = [Fore.GREEN + '✓ ' + Fore.RESET]


class AppFileError(OSError):
    pass


def download_resources(url: str, soup: Any, full_path_to_dir: str, dir_name: str) -> Any:  # noqa C901
    """Downloads resources from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            soup(Any): content of html file
            full_path_to_dir(str): path to directory where local resources are saved  # noqa E501
            dir_name(str): name of directory where local resources are saved

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
            logger_pars.error(f"{e} :: link: '{link_to_resource}'")
            continue

        file_name = make_file_name(link_to_resource)
        change_link_to_file_path(dir_name, tag, file_name)

        spinner.next()
        print(link_to_resource)

        write_content_of_resource_to_file(full_path_to_dir, file_name, response)

    return soup


def is_local_resource(url: str, link_to_resource: str) -> bool:
    """Checks is the local domain of the resource """
    if urlparse(url).netloc != urlparse(link_to_resource).netloc:
        return False
    return True


def request_link_to_resource(link_to_resource: str) -> Any:
    """Make a request for a link with a resource."""
    logger_pars.debug(f'link to download is {link_to_resource}')
    response = requests.get(link_to_resource, stream=True)
    response.raise_for_status()
    return response


def write_content_of_resource_to_file(dir: str,
                                      file_name: str,
                                      response: Any) -> None:
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
    except requests.RequestException as err:
        logger_pars.error(f'Unknown error: {err}')
        raise AppFileError(err) from err
    except OSError as e:
        logger_pars.error(f'Unknown error: {e}-{path_to_resource}')
        raise AppFileError(e) from e


def get_links_and_tags_of_resources(soup: Any,
                                    url: str) -> List[Tuple[str, Any]]:
    """Make list of links to resources
       and tags with this links
       and add domain to link if absent
    """
    tags = {IMG: SRC, SCRIPT: SRC, LINK: HREF}
    links_and_tags_of_resourses = []
    for tag in tags:
        for source in soup.find_all(tag):
            if tag and tags[tag]:
                links_and_tags_of_resourses.append(
                    (urljoin(
                        url, source.get(tags[tag])
                    ), source)
                )
    return links_and_tags_of_resourses


def make_file_name(url: str) -> str:
    """Make file name from link to resource."""
    suffix = Path(url).suffix.lower()
    netloc = urlparse(url).netloc
    path = urlparse(url).path

    url_without_scheme = '{}{}'.format(netloc, path)
    url_without_suffix = '{}/{}'.format(Path(url_without_scheme).parent,
                                        Path(url_without_scheme).stem)
    update_url = re.sub(r'\W', '-', url_without_suffix)
    if not suffix:
        return '{}.html'.format(update_url)
    return '{}{}'.format(update_url, suffix)


def change_link_to_file_path(dir_name: str, tag: Any, file_name: str) -> None:
    """Changes link to resources."""
    tags = {IMG: SRC, SCRIPT: SRC, LINK: HREF}
    if tag.name in tags:
        subtag = tags[tag.name]
        tag[subtag] = os.path.join(dir_name, file_name)
