import pytest
from click.testing import CliRunner

from vl import cli


def reset_globals():
    cli.ERRORS = []
    cli.DUPES = []
    cli.EXCEPTIONS = []
    cli.WHITELISTED = []


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def valid_urls():
    return """
Valid Urls
==========

* [Test Link1](http://httpbin.org/status/200)
* [Test Link2](http://httpbin.org/status/201)
* [Test Link3](http://httpbin.org/status/204)
"""


@pytest.fixture
def valid_urls_with_static(): # flake8: noqa
    return """
Valid Urls
==========

* [Test Link1](http://httpbin.org/status/200)
* [Test Link2](http://httpbin.org/status/201)
* [Test Link3](http://httpbin.org/status/204)
* [Test Link4](https://www.google.com.br/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png)
"""


@pytest.fixture
def some_errors():
    return """
Valid Urls and Some Errors
==========================

* [Test Link1](http://httpbin.org/status/200)
* [Bad Link](http://httpbin.org/status/400)
* [Bad Link2](http://httpbin.org/status/401)
* [Bad Link3](http://httpbin.org/status/402)
* [Bad Link5](http://httpbin.org/status/403)
* [Bad Link6](http://httpbin.org/status/404)
* [Bad Link3](http://httpbin.org/status/405)
* [Exception](http://httpbin.org/delay/10)
* [Test Link2](http://httpbin.org/status/201)
* [No Scheme](httpbin.org/status/204)
"""


@pytest.fixture
def dupes():
    return """
Valid Urls With Some Dupes
==========================

* [Dupe](http://httpbin.org/status/200)
* [Dupe1](http://httpbin.org/status/200)
* [Dupe2](http://httpbin.org/status/200)
* [Test Link2](http://httpbin.org/status/201)
"""


@pytest.fixture
def whitelists():
    return """
Valid Urls With Some Dupes
==========================

* [link1](http://httpbin.org/status/200)
* [link2](http://httpbin.org/status/201)
* [link3](http://httpbin.org/status/204)
"""


def test_cli_no_args(runner):
    reset_globals()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2


def test_cli_bad_allow_codes(runner, valid_urls):
    reset_globals()
    with runner.isolated_filesystem():
        with open('valid_urls.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['valid_urls.md', '--debug',
                                          '--allow-codes', '123-456'])
        assert result.exit_code == 2


def test_cli_with_valid_urls(runner, valid_urls):
    reset_globals()
    with runner.isolated_filesystem():
        with open('valid_urls.md', 'w') as f:
            f.write(valid_urls)

        result = runner.invoke(cli.main, ['valid_urls.md', '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 0


def test_cli_with_valid_and_bad_urls(runner, some_errors):
    reset_globals()
    with runner.isolated_filesystem():
        with open('some_errors.md', 'w') as f:
            f.write(some_errors)

        result = runner.invoke(cli.main, ['some_errors.md', '--debug'])
        assert result.exit_code == 1
        assert len(cli.ERRORS) == 6
        assert len(cli.EXCEPTIONS) == 1
        assert len(cli.DUPES) == 0


def test_cli_with_dupes(runner, dupes):
    reset_globals()
    with runner.isolated_filesystem():
        with open('dupes.md', 'w') as f:
            f.write(dupes)

        result = runner.invoke(cli.main, ['dupes.md', '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 1


def test_cli_with_allow_codes(runner):
    reset_globals()
    urls = """
Valid and Allow
===============

* [Test Link1](http://httpbin.org/status/200)
* [Test Link2](http://httpbin.org/status/201)
* [Test Link3](http://httpbin.org/status/204)
* [Test Link3](http://httpbin.org/status/404)
* [Test Link3](http://httpbin.org/status/500)
"""


    with runner.isolated_filesystem():
        with open('valid.md', 'w') as f:
            f.write(urls)

        result = runner.invoke(cli.main, ['valid.md', '-a 404,500',
                                          '--debug'])

        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 0


def test_cli_with_whitelist(runner, whitelists):
    reset_globals()
    with runner.isolated_filesystem():
        with open('whitelist.md', 'w') as f:
            f.write(whitelists)

        result = runner.invoke(cli.main, ['whitelist.md', '-w httpbin.org/status/201',
                                          '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.DUPES) == 0
        assert len(cli.WHITELISTED) == 1


def test_cli_with_bad_whitelist(runner, whitelists):
    reset_globals()
    with runner.isolated_filesystem():
        with open('whitelist.md', 'w') as f:
            f.write(whitelists)

        result = runner.invoke(cli.main, ['whitelist.md', '--whitelist ',
                                          '--debug'])
        assert result.exit_code == 2


def test_cli_with_static(runner, valid_urls_with_static):
    reset_globals()
    with runner.isolated_filesystem():
        with open('with_static.md', 'w') as f:
            f.write(valid_urls_with_static)

        result = runner.invoke(cli.main, ['with_static.md', '--debug'])
        assert result.exit_code == 0
        assert len(cli.ERRORS) == 0
        assert len(cli.EXCEPTIONS) == 0
        assert len(cli.STATICS) == 1
