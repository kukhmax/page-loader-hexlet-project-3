from page_loader.engine import download_html, update_url_to_file_name
from page_loader.engine import make_prettify
from page_loader.parser_images import download_images
from page_loader.parser_resources import download_resources
from page_loader.utilities import make_dir_and_soup
import requests_mock
import pytest
import re


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
            mock.get('https://ru.hexlet.io/courses', text=text)
            path_to_html = download_html('https://ru.hexlet.io/courses',
                                         tmp_path)
        soup, dir = make_dir_and_soup(path_to_html)
        soup = download_resources(
            'https://ru.hexlet.io/courses', soup, dir
        )
        path_to_html = make_prettify(path_to_html, soup)
        with open(path_to_html) as f:
            content = f.read()
            res = re.sub(r'(?<=src=\"|ref=\")[\/\-\_a-zA-Z0-9]{0,}(?=ru-hexlet-io-courses_f)', '', content)  # noqa E501
            with open('tests/fixtures/scripts_result.html') as f1:
                assert res == f1.read()
