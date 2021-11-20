from page_loader.engine import download, update_url_to_file_name
from urllib.parse import urljoin
from tempfile import TemporaryDirectory
import requests_mock
import pytest
import os
from page_loader.settings_log import logger_config
import logging.config

logging.config.dictConfig(logger_config)

test_logger = logging.getLogger('app_logger.test')


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
     'tmp/tmp/cdn2-hexlet-io-courses.html'),
])
def test_output(url, path_to_dir, result):
    assert update_url_to_file_name(url, path_to_dir) == result


def test_download(tmp_path):
    """Tests function 'download'
       and
       tests correct download resources.
    """
    with open('tests/fixtures/resources.html') as f:
        text = f.read()
    with open('tests/fixtures/script.js') as f1:
        js_code = f1.read()

    with requests_mock.Mocker() as mock:
        mock.get('https://page-loader.hexlet.repl.co', text=text)
        mock.get('https://page-loader.hexlet.repl.co/assets/professions/nodejs.png')  # noqa E501
        mock.get('https://page-loader.hexlet.repl.co/script.js', text=js_code)
        mock.get('https://page-loader.hexlet.repl.co/assets/application.css')  # noqa E501
        mock.get('https://page-loader.hexlet.repl.co/courses')
        path_to_html = download(
            'https://page-loader.hexlet.repl.co', tmp_path
        )
        path_to_script = os.path.join(
            tmp_path,
            'page-loader-hexlet-repl-co_files/page-loader-hexlet-repl-co-script.js'  # noqa E501
        )
        assert os.path.exists(path_to_script)
        with open('tests/fixtures/script.js') as script:
            with open(path_to_script) as test:
                assert script.read() == test.read()
        with open(path_to_html) as f:
            content = f.read()
            with open('tests/fixtures/resources_result.html') as f1:
                assert content == f1.read()


@pytest.mark.parametrize('code', [404, 500])
def test_response_with_error(requests_mock, code):
    url = urljoin("https://ru.hexlet.io/courses", str(code))
    requests_mock.get(url, status_code=code)

    with TemporaryDirectory() as tmpdirname:
        with pytest.raises(Exception):
            assert download(url, tmpdirname)
