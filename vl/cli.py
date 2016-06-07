#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import time
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
                     r'+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')
ERRORS = []
EXCEPTIONS = []


def handle_exception(request, exception):
    EXCEPTIONS.append((request.url, exception))


def is_static(url):
    # TODO: try to find a better way of getting static files
    static = ('zip', 'xml', 'jpg', 'jpeg', 'gif', 'svg', 'webm')
    path = urlparse(url).path
    return path.endswith(static)


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
def main(doc, timeout, size, debug):
    """Main CLI method"""
    t1 = time.time()
    links = [i[0] for i in LINK_RE.findall(doc.read())]
    # no static
    links = list(filter(lambda x: not is_static(x), links))
    requests = (grequests.get(u, timeout=timeout) for u in links)
    responses = grequests.imap(requests, exception_handler=handle_exception,
                               size=size)

    colors = {
        200: 'green',
        301: 'green',
        403: 'red',
        404: 'red',
        500: 'red',
        503: 'red',
        502: 'red'
    }
    error_codes = [400, 403, 500, 502, 503, 404]

    for res in responses:
        if res.status_code in error_codes:
            ERRORS.append((res.status_code, res.url))

        url = click.style('{0}'.format(res.url), fg='white')
        status = click.style(str(res.status_code), fg=colors[res.status_code],
                             bold=True)
        click.secho('- {0} {1}'.format(url, status), fg='green')

    errors_len = len(ERRORS)
    exceptions_len = len(EXCEPTIONS)

    if errors_len:
        click.echo()
        click.echo('Failed URLs:')
        for code, url in ERRORS:
            code = click.style('{0}'.format(code), bold=True)
            click.secho('- {0} {1}'.format(url, code), fg='red')

    if exceptions_len and debug:
        click.echo()
        click.echo('Exceptions raised:')
        for url, exception in EXCEPTIONS:
            click.echo('- {0}'.format(url))
            click.secho('{0}'.format(exception), fg='red', bold=True)
            click.echo()

    click.secho('Total Links Parsed {0}'.format(len(links)), fg='green')
    click.secho('Total Errors {0}'.format(errors_len), fg='red')
    click.secho('Total Exceptions {0}'.format(exceptions_len), fg='red')

    if debug:
        click.echo('Execution time: {0:.2f} seconds'.format(time.time() - t1))

    if errors_len or exceptions_len:
        sys.exit(1)

if __name__ == "__main__":
    main()
