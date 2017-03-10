import pytest
import responses
from requests.exceptions import HTTPError
from click.testing import CliRunner

from vl import cli


def reset_globals():
    cli.ERRORS = []
    cli.DUPES = []
    cli.EXCEPTIONS = []
    cli.WHITELISTED = []
    cli.STATICS = []


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def valid_urls():
    return """
Valid Urls
==========

* [Test Link1](http://www.test1.com)
* [Test Link2](http://www.test2.com)
* [Test Link3](http://www.test3.com)
"""


@pytest.fixture
def valid_urls_with_static():
    return """
Valid Urls
==========

* [Test Link1](http://www.test1.com)
* [Test Link2](http://www.test2.com)
* [Test Link3](http://www.test3.com)
* [Test Link4](http://www.test3.com/1.gif)
"""


@pytest.fixture
def some_errors():
    return """
Valid Urls and Some Errors
==========================

* [Test Link1](http://www.test1.com)
* [Bad Link](http://www.badlink1.com)
* [Bad Link2](http://www.badlink2.com)
* [Bad Link3](http://www.badlink3.com)
* [Bad Link3](http://www.badlink4.com)
* [Bad Link5](http://www.badlink5.com)
* [Bad Link6](http://www.badlink6.com)
* [Bad Link7](http://www.badlink7.com)
* [Bad Link8](http://www.badlink8.com)
* [Bad Link9](http://www.badlink9.com)
* [Exception](http://www.exception.com)
* [Test Link2](http://www.test2.com)
* [No Scheme](www.test2.com)
"""


@pytest.fixture
def dupes():
    return """
Valid Urls With Some Dupes
==========================

* [Dupe1](http://www.dupe1.com)
* [Dupe1](http://www.dupe1.com)
* [Dupe1](http://www.dupe1.com)
* [Test Link2](http://www.test2.com)
"""


@pytest.fixture
def whitelists():
    return """
Valid Urls With Some Dupes
==========================

* [link1](http://www.test.com)
* [link2](http://www.whitelisted.com)
* [link3](http://whitelisted.com)
* [link4](http://whitelisted.com/test.html)
* [link5](http://test.whitelisted.com/?arg=1&arg=2)
* [link6](http://white-listed.com/)
* [link7](http://www.test2.com)
"""


def test_cli_no_args(runner):
    reset_globals()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2


def test_cli_bad_allow_codes(runner, valid_urls):
    reset_globals()
    urls = (
        ('http://www.test1.com', 200),
        ('http://www.test2.com', 200),
        ('http://www.test3.com', 200),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('valid_urls.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['valid_urls.md', '--debug',
                                          '--allow-codes', '123-456'])
        assert result.exit_code == 2


@responses.activate
def test_cli_with_valid_urls(runner, valid_urls):
    reset_globals()
    urls = (
        ('http://www.test1.com', 200),
        ('http://www.test2.com', 200),
        ('http://www.test3.com', 200),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('valid_urls.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['valid_urls.md', '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 0


@responses.activate
def test_cli_with_valid_and_bad_urls(runner, some_errors):
    reset_globals()
    urls = (
        ('http://www.test1.com', 200),
        ('http://www.test2.com', 200),
        ('http://www.badlink1.com', 500),
        ('http://www.badlink2.com', 501),
        ('http://www.badlink3.com', 502),
        ('http://www.badlink4.com', 503),
        ('http://www.badlink5.com', 504),
        ('http://www.badlink6.com', 401),
        ('http://www.badlink7.com', 402),
        ('http://www.badlink8.com', 404),
        ('http://www.badlink9.com', 409),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    exception = HTTPError('BAD!')
    responses.add(responses.HEAD, 'http://www.exception.com',
                  body=exception)

    with runner.isolated_filesystem():
        with open('some_errors.md', 'w') as f:
            f.write(some_errors)

        result = runner.invoke(cli.main, ['some_errors.md', '--debug'])
        assert result.exit_code == 1
        assert len(cli.ERRORS) == 9
        assert len(cli.EXCEPTIONS) == 1
        assert len(cli.DUPES) == 0


@responses.activate
def test_cli_with_dupes(runner, dupes):
    reset_globals()
    urls = (
        ('http://www.dupe1.com', 200),
        ('http://www.test2.com', 200),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('dupes.md', 'w') as f:
            f.write(dupes)

        result = runner.invoke(cli.main, ['dupes.md', '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 1


@responses.activate
def test_cli_with_allow_codes(runner, valid_urls):
    reset_globals()
    urls = (
        ('http://www.test1.com', 200),
        ('http://www.test3.com', 500),
        ('http://www.test2.com', 404),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('valid.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['valid.md', '-a 404,500',
                                          '--debug'])

        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 0
        assert len(cli.WHITELISTED) == 2


@responses.activate
def test_cli_with_whitelist(runner, whitelists):
    reset_globals()
    urls = (
        ('http://www.test.com', 200),
        ('http://www.whitelisted.com', 200),
        ('http://whitelisted.com', 200),
        ('http://whitelisted.com/test.html', 200),
        ('http://test.whitelisted.com/', 200),
        ('http://white-listed.com/', 200),
        ('http://www.test2.com', 200),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('whitelist.md', 'w') as f:
            f.write(whitelists)

        result = runner.invoke(cli.main, ['whitelist.md', '-w whitelisted.com',
                                          '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 0
        assert len(cli.WHITELISTED) == 4


@responses.activate
def test_cli_with_bad_whitelist(runner, whitelists):
    reset_globals()
    urls = (
        ('http://www.test.com', 200),
        ('http://www.whitelisted.com', 200),
        ('http://whitelisted.com', 200),
        ('http://whitelisted.com/test.html', 200),
        ('http://test.whitelisted.com/', 200),
        ('http://white-listed.com/', 200),
        ('http://www.test2.com', 200),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('whitelist.md', 'w') as f:
            f.write(whitelists)

        result = runner.invoke(cli.main, ['whitelist.md', '--whitelist ',
                                          '--debug'])
        assert result.exit_code == 2


@responses.activate
def test_cli_with_static(runner, valid_urls_with_static):
    reset_globals()
    urls = (
        ('http://www.test1.com', 200),
        ('http://www.test2.com', 200),
        ('http://www.test3.com', 200),
        ('http://www.test3.com/1.gif', 200),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('with_static.md', 'w') as f:
            f.write(valid_urls_with_static)

        result = runner.invoke(cli.main, ['with_static.md', '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.STATICS) == 1


@responses.activate
def test_cli_with_errors_only(runner, valid_urls):
    reset_globals()
    urls = (
        ('http://www.test1.com', 400),
        ('http://www.test2.com', 500),
        ('http://www.test3.com', 103),
    )
    for url, code in urls:
        responses.add(responses.HEAD, url, status=code)

    with runner.isolated_filesystem():
        with open('errors.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['errors.md', '--debug'])
        assert result.exit_code == 1
        assert len(cli.ERRORS) == 3
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.STATICS) == 0


@responses.activate
def test_cli_with_good_codes_on_allow_codes(runner, valid_urls):
    reset_globals()
    with runner.isolated_filesystem():
        with open('errors.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['errors.md', '-a 200,301',
                                          '--debug'])
        assert result.exit_code == 2
