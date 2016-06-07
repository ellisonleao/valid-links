from __future__ import print_function

import pytest
import responses
from requests.exceptions import HTTPError
from click.testing import CliRunner

from vl import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_no_args(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 2


@responses.activate
def test_cli_with_valid_urls(runner):
    valid_urls = [
        'http://www.test1.com',
        'http://www.test2.com',
        'http://www.test3.com',
    ]
    for url in valid_urls:
        responses.add(responses.GET, url, status=200)

    result = runner.invoke(cli.main, ['tests/valid_urls.md'])

    assert result.exit_code == 0


@responses.activate
def test_cli_with_valid_and_bad_urls(runner):
    urls = [
        ('http://www.test1.com', 200),
        ('http://www.test2.com', 200),
        ('http://www.badlink1.com', 403),
        ('http://www.badlink2.com', 404),
        ('http://www.badlink3.com', 503),
        ('http://www.badlink4.com', 500),
    ]
    for url, code in urls:
        responses.add(responses.GET, url, status=code)

    exception = HTTPError('BAD!')
    responses.add(responses.GET, 'http://www.exception.com',
                  body=exception)

    result = runner.invoke(cli.main, ['tests/some_errors.md', '--debug'])
    assert result.exit_code == 1
    assert len(cli.ERRORS) == 4
    assert len(cli.EXCEPTIONS) == 1
