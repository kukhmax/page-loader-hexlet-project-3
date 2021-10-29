from page_loader.engine import download_html, update_url_to_file_name
from page_loader.engine import make_prettify
from page_loader.parser_images import download_images
from page_loader.parser_resources import download_resources
from page_loader.utilities import make_dir_and_soup
from page_loader.engine import download
from urllib.parse import urljoin
from tempfile import TemporaryDirectory
import requests_mock
import requests
import pytest
import re
from page_loader.settings_log import logger_config
import logging.config

logging.config.dictConfig(logger_config)

logger = logging.getLogger('app_logger')


@pytest.mark.parametrize('url, path_to_dir, result', [
    ('https://cdn2.hexlet.io/courses',
     'var/tmp',
     'var/tmp/cdn2-hexlet-io-courses.html'),
    ('http://cdn2.hexlet.io/courses',
     'var/tmp',
     'var/tmp/cdn2-hexlet-io-courses.html'),
    ('cdn2.hexlet.io/courses/https://end',
     'var/bin',
     'var/bin/cdn2-hexlet-io-courses-https---end.html'),
    ('https://cdn2.hexlet.io/courses.html',
     'tmp/tmp',
     'tmp/tmp/cdn2-hexlet-io-courses-html.html'),
])
def test_output(url, path_to_dir, result):
    assert update_url_to_file_name(url, path_to_dir) == result


def test_download_html(requests_mock, tmp_path):
    requests_mock.get('https://ru.hexlet.io/courses', text='<!DOCTYPE html>')
    path_to_tmp_file = download_html('https://ru.hexlet.io/courses', tmp_path)
    with open(path_to_tmp_file) as f:
        assert f.read() == '<!DOCTYPE html>'


def test_download_image(tmp_path):
    with open('tests/fixtures/image.html') as f:
        text = f.read()
        with requests_mock.Mocker() as mock:
            mock.get('https://ru.hexlet.io/courses', text=text)
            path_to_html = download_html('https://ru.hexlet.io/courses',
                                         tmp_path)
        soup, dir = make_dir_and_soup(path_to_html)
        soup = download_images(
            'https://ru.hexlet.io/courses', path_to_html, soup, dir
        )
        path_to_html = make_prettify(path_to_html, soup)
        with open(path_to_html) as f:
            file = f.read()
            res = re.sub(r'(?<=src=")([\/\-\_a-zA-Z0-9]){,}(?=ru-hexlet-io-c)',
                         '', file)
            with open('tests/fixtures/image_result.html') as f1:
                assert res == f1.read()


def test_download_resourses(tmp_path):
    with open('tests/fixtures/scripts.html') as f:
        text = f.read()
        with requests_mock.Mocker() as mock:
            mock.get('https://page-loader.hexlet.repl.co', text=text)
            path_to_html = download_html(
                'https://page-loader.hexlet.repl.co', tmp_path
            )
        try:
            soup, dir = make_dir_and_soup(path_to_html)
            soup = download_resources(
                'https://page-loader.hexlet.repl.co', soup, dir
            )
        except Exception as e:
            logger.error(f'Unknown error: {e}')
        path_to_html = make_prettify(path_to_html, soup)
        with open(path_to_html) as f:
            content = f.read()
            with open('tests/fixtures/scripts_result.html') as f1:
                assert content == f1.read()


def test_isexceptions(tmp_path):
    with requests_mock.Mocker() as mock:
        url = "https://ru.hexlet.io/courses"
        mock.register_uri('GET', url, exc=requests.HTTPError)
        with pytest.raises(requests.HTTPError) as excinfo:
            download_html(url, tmp_path)
        assert excinfo.type is requests.HTTPError


@pytest.mark.parametrize('code', [404, 500])
def test_response_with_error(requests_mock, code):
    url = urljoin("https://ru.hexlet.io/courses", str(code))
    requests_mock.get(url, status_code=code)

    with TemporaryDirectory() as tmpdirname:
        with pytest.raises(Exception):
            assert download(url, tmpdirname)
