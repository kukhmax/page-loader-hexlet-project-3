#!usr/bin/env python3

import os
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
from page_loader.utilities import get_resourсe_url
from typing import Any, List, Tuple


def download_scripts(url: str, path_to_html: str, soup: Any, dir: str) -> Any:
    """Downloads scripts and links from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            path_to_html(str): path to the saved html file
            soup(Any): content of html file
            dir(str): path to directory where local resources are saved

        Retruns:
            path_to_html(str): path to the modified html file
    """
    list_of_links = get_links(soup)
    for link in list_of_links:
        link_to_resource = get_resourсe_url(url, link[0])
        if link_to_resource:
            response = requests.get(link_to_resource)
            suffix = Path(link_to_resource).suffix
            if not suffix:
                link_to_resource += '.html'
            tmp = re.sub(r'[^a-zA-Z0-9]+', '-',
                         f'{urlparse(link_to_resource).netloc}\
{urlparse(link_to_resource).path}').rsplit('-', 1)
            file_name = f'{tmp[0]}.{tmp[1]}'
            path_to_resource = os.path.join(dir, file_name)
            if link[1] == 'script':
                soup.find(src=link[0])['src'] = path_to_resource
            elif link[1] == 'link':
                soup.find(href=link[0])['href'] = path_to_resource
            with open(path_to_resource, 'wb') as file:
                file.write(response.content)
    return soup


def get_links(soup: Any) -> List[Tuple[Any, str]]:
    """Get list of links to resources"""
    list_of_links = []
    if soup('script'):
        for script in soup('script'):
            list_of_links.append((script.get('src'), 'script'))
    if soup('link'):
        for link in soup('link'):
            list_of_links.append((link.get('href'), 'link'))
    return list_of_links
