#!usr/bin/env python3

import os
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
from page_loader.utilities import get_resourсe_url, AppError
from typing import Any, List, Tuple
import logging
from progress.spinner import Spinner


logger_pars = logging.getLogger('app_logger.pars')

SRC, IMG, SCRIPT, HREF, LINK = 'src', 'img', 'script', 'href', 'link'


class MySpinner(Spinner):
    phases = ['\x1b[3m\x1b[32m✓ ']


def download_resources(url: str, soup: Any, dir: str) -> Any:  # noqa C901
    """Downloads scripts and links from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            soup(Any): content of html file
            dir(str): path to directory where local resources are saved

        Retruns:
            path_to_html(str): path to the modified html file
    """
    list_of_links = get_links(url, soup)
    spinner = MySpinner(' ')
    state = 'go'
    while state != 'FINISHED':
        for link in list_of_links:
            link_to_resource = get_resourсe_url(url, link[0])
            try:
                logger_pars.debug(f'link is {link_to_resource}')
                response = requests.get(link_to_resource)
                response.raise_for_status()
                logger_pars.debug(
                    f'status is {requests.get(link_to_resource).status_code}'
                )
            except (requests.exceptions.MissingSchema,
                    requests.exceptions.InvalidSchema,
                    requests.exceptions.InvalidURL) as e:
                logger_pars.error(e)
                raise AppError('Wrong address!') from e
            except requests.exceptions.HTTPError as e:
                logger_pars.error(e)
                raise AppError(f'Connection failed. Status code is \
{requests.get(link_to_resource).status_code}') from e
            except requests.exceptions.RequestException as e:
                logger_pars.error(f'Error is {e}')
                raise AppError(f'Erro r is {e}') from e

            suffix = Path(link_to_resource).suffix.lower()
            netloc = urlparse(link_to_resource).netloc
            path = urlparse(link_to_resource).path

            if suffix == ".png" or suffix == ".jpg":
                file_name = re.sub(r'\-(?=(png|jpg)$)', '.',
                                   re.sub(r"[^a-zA-Z0-9]+", '-',
                                          f'{netloc}{path}'))

            if not suffix:
                path += '.html'
            tmp = re.sub(r'[^a-zA-Z0-9]+', '-',
                         f'{netloc}{path}').rsplit('-', 1)
            file_name = f'{tmp[0]}.{tmp[1]}'
            work_dir = re.sub(r'[\/\-\_a-zA-Z0-9]{0,}(?=\/)\/', '', dir)
            path_to_resource = os.path.join(dir, file_name)
            if link[1] == SCRIPT or link[1] == IMG:
                soup.find(src=link[0])[SRC] = os.path.join(work_dir,
                                                           file_name)
            elif link[1] == LINK:
                soup.find(href=link[0])[HREF] = os.path.join(work_dir,
                                                             file_name)
            spinner.next()
            print('\x1b[1m\x1b[37m', link_to_resource)

            with open(path_to_resource, 'wb') as file:
                try:
                    file.write(response.content)
                except PermissionError:
                    logger_pars.error('PermissionError')
                    raise PermissionError("You don't have permission")
        state = 'FINISHED'
    return soup


def get_links(url: str, soup: Any) -> List[Tuple[Any, str]]:
    """Get list of links to resources"""
    img_list = [(img.get(SRC), IMG) for img in soup(IMG) if soup(IMG)]
    script_list = [
        (img.get(SRC), SCRIPT) for img in soup(SCRIPT) if soup(SCRIPT)
    ]
    link_list = [
        (img.get(HREF), LINK) for img in soup(LINK) if soup(LINK)
    ]
    links = img_list + script_list + link_list
    return [
        link for link in links if get_resourсe_url(url, link[0])
    ]
