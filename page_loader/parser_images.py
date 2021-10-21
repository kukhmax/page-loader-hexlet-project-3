#!usr/bin/env python3

from bs4 import BeautifulSoup
import os
import requests
import re
from page_loader.engine import download
from pathlib import Path
from urllib.parse import urlparse
PWD = os.getcwd()


def get_image_url(url, src):
    domain = urlparse(url).netloc
    src_netloc = urlparse(src).netloc
    if src_netloc == domain:
        return src
    elif src_netloc == '':
        return f'https://{domain}{src}'
    else:
        return None


def download_images(url, path_to_html, path):
    with open(path_to_html) as f:
        dir = re.sub('.html$', '_files', path_to_html)
        os.mkdir(dir)
        soup = BeautifulSoup(f, 'html.parser')
        for img in soup('img'):
            src = img.get('src')
            link_to_image = get_image_url(url, src)
            if link_to_image:
                suffix = Path(src).suffix.lower()
                if suffix == ".png" or suffix == ".jpg":
                    response = requests.get(link_to_image)
                    file_name = re.sub(r'\-(?=(png|jpg)$)', '.',
                                    re.sub(r"[^(a-zA-Z0-9]+", '-', src))
                    path_to_image = os.path.join(dir, file_name)
                    tag = soup.find(src=src)
                    tag['src'] = path_to_image
                    with open(path_to_image, 'wb') as file:
                        file.write(response.content)

    with open(path_to_html, 'w+') as update_file:
        update_file.write(soup.prettify())
    return path_to_html

# path = download('https://python-scripts.com/beautifulsoup-html-parsing', PWD )
# download_images('https://python-scripts.com/beautifulsoup-html-parsing', path, PWD)