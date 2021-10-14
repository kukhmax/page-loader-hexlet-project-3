from page_loader.engine import download, update_url_to_file_path
import pytest


@pytest.mark.parametrize('url, path_to_dir, result', [
    ('https://ru.hexlet.io/courses',
     'var/tmp',
     'var/tmp/ru-hexlet-io-courses.html'),
    ('http://ru.hexlet.io/courses',
     'var/tmp',
     'var/tmp/ru-hexlet-io-courses.html'),
    ('ru.hexlet.io/courses/https://end',
     'var/bin',
     'var/bin/ru-hexlet-io-courses-https---end.html'),
    ('https://ru.hexlet.io/courses.html',
     'tmp/tmp',
     'tmp/tmp/ru-hexlet-io-courses-html.html'),
])
def test_output(url, path_to_dir, result):
    assert update_url_to_file_path(url, path_to_dir) == result


def test_download(requests_mock, tmp_path):
    requests_mock.get('https://ru.hexlet.io/courses', text='<!DOCTYPE html>')
    path_to_tmp_file = download('https://ru.hexlet.io/courses', tmp_path)
    with open(path_to_tmp_file) as f:
        with open('tests/fixtures/test.html') as f1:
            assert f.read() == f1.read()
