#!usr/bin/env python3

import os
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
from page_loader.utilities import get_resourсe_url


def download_images(url, path_to_html, soup, dir):
    """Downloads images from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            path_to_html(str): path to the saved html file

        Retruns:
            path_to_html(str): path to the modified html file
    """
    for img in soup('img'):
        src = img.get('src')
        link_to_image = get_resourсe_url(url, src)
        if link_to_image:
            suffix = Path(src).suffix.lower()
            if suffix == ".png" or suffix == ".jpg":
                response = requests.get(link_to_image)
                file_name = re.sub(r'\-(?=(png|jpg)$)', '.',
                                   re.sub(r"[^a-zA-Z0-9]+", '-',
                                          f'{urlparse(link_to_image).netloc}\
{urlparse(link_to_image).path}'))
                path_to_image = os.path.join(dir, file_name)
                tag = soup.find(src=src)
                tag['src'] = path_to_image
                with open(path_to_image, 'wb') as file:
                    file.write(response.content)
    return soup
