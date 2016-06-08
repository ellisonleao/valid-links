#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import time
from collections import Counter

try:
    from urlparse import urlparse
except ImportError:
    # py3
    from urllib.parse import urlparse

import click
import grequests

LINK_RE = re.compile(r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www'
                     r'\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]'
                     r'+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]'
                     r'+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]'
                     r'))')
ERROR_CODE_RE = re.compile(r'([4|5][\d]{2})')

ERRORS = []
EXCEPTIONS = []
DUPES = []


def handle_exception(request, exception):
    EXCEPTIONS.append((request.url, exception))


def is_static(url):
    # TODO: try to find a better way of getting static files
    static = ('zip', 'xml', 'jpg', 'jpeg', 'gif', 'svg', 'webm')
    path = urlparse(url).path
    return path.endswith(static)


def validade_allowed_codes(ctx, param, value):
    if not value:
        return
    try:
        codes = value.split(',')
        codes = list(filter(lambda x: ERROR_CODE_RE.match(x), codes))
    except ValueError:
        raise click.BadParameter('--allow-codes param must be comma splitted')
    return value


@click.command()
@click.argument('doc', type=click.File())
@click.option('timeout', '-t', '--timeout', default=2.0, type=click.FLOAT,
              help='request timeout arg. Default is 2 seconds')
@click.option('size', '-s', '--size', default=100, type=click.INT,
              help=('Specifies the number of requests to make at a time. '
                    'default is 100'))
@click.option('-d', '--debug', is_flag=True,
              help=('Prints out some debug information like execution time'
                    ' and exception messages'))
@click.option('allow_codes', '-a', '--allow-codes',
              callback=validade_allowed_codes, help=('A comma splitted http '
                                                     'response allowed codes'))
def main(doc, timeout, size, debug, allow_codes):
    """
    Examples:
    simple call
    $ vl README.md

    Adding debug outputs

    $ vl README.md --debug

    Adding a custom timeout for each url. time on seconds.

    $ vl README.md -t 3

    Adding a custom size param, to add more requests per time

    $ vl README -s 1000

    Skipping some error codes. This will allow 500 and 404 responses to
    be ignored

    $ vl README.md -a 500,404
    """
    t1 = time.time()
    links = [i[0] for i in LINK_RE.findall(doc.read())]
    allow_codes = allow_codes or []
    counts = Counter(links)
    counts_keys = counts.keys()
    DUPES.extend([i for i in counts_keys if counts[i] > 1])

    # no static
    links = list(filter(lambda x: not is_static(x), links))

    # no dupes
    links = set(list(links))

    requests = (grequests.get(u, timeout=timeout) for u in links)
    responses = grequests.imap(requests, exception_handler=handle_exception,
                               size=size)

    for res in responses:
        status_code = str(res.status_code)
        is_error_code = ERROR_CODE_RE.match(status_code)
        if is_error_code and status_code not in allow_codes:
            ERRORS.append((res.status_code, res.url))
            color = 'red'
        else:
            color = 'green'

        url = click.style('{0}'.format(res.url), fg='white')
        status = click.style(str(res.status_code), fg=color, bold=True)
        click.secho('- {0} {1}'.format(url, status), fg='green')

    errors_len = len(ERRORS)
    exceptions_len = len(EXCEPTIONS)
    dupes_len = len(DUPES)

    if errors_len:
        click.echo()
        click.echo('Failed URLs:')
        for code, url in ERRORS:
            code = click.style('{0}'.format(code), bold=True)
            click.secho('- {0} {1}'.format(url, code), fg='red')

    if exceptions_len and debug:
        click.echo()
        click.echo('Exceptions raised:')
        click.secho('Check URLs for possible false positives', fg='yellow')
        click.echo()
        for url, exception in EXCEPTIONS:
            click.echo('- {0}'.format(url))
            click.secho('{0}'.format(exception), fg='red', bold=True)
            click.echo()

    if dupes_len and debug:
        click.echo()
        click.echo('Dupes:')
        for url in DUPES:
            click.secho('- {0}'.format(url), fg='yellow')

    click.secho('Total Links Parsed {0}'.format(len(links)), fg='green')
    click.secho('Total Errors {0}'.format(errors_len), fg='red')
    click.secho('Total Exceptions {0}'.format(exceptions_len), fg='red')
    click.secho('Total Dupes {0}'.format(dupes_len), fg='yellow')

    if debug:
        click.echo('Execution time: {0:.2f} seconds'.format(time.time() - t1))

    if errors_len or exceptions_len or dupes_len:
        sys.exit(1)

if __name__ == "__main__":
    main()
