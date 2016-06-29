#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import time
import six

# flake8: noqa
if six.PY2:
    from urlparse import urlparse
    strip_func = unicode.strip
else:
    from urllib.parse import urlparse
    strip_func = str.strip

import click
import grequests

# globals
# flake8: noqa
LINK_RE = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')
ERROR_CODE_RE = re.compile(r'([4|5][\d]{2})')
ERRORS = []
EXCEPTIONS = []
DUPES = []
WHITELISTED = []


def handle_exception(request, exception):
    EXCEPTIONS.append((request.url, exception))


def is_static(url):
    # TODO: try to find a better way of getting static files
    static = ('zip', 'xml', 'jpg', 'jpeg', 'gif', 'svg', 'webm')
    path = urlparse(url).path
    return path.endswith(static)


def validate_allowed_codes(ctx, param, value):
    if not value:
        return []
    try:
        codes = value.split(',')
        codes = list(map(strip_func, codes))
        codes = list(filter(lambda x: ERROR_CODE_RE.match(x), codes))
        return codes
    except ValueError:
        raise click.BadParameter('--allow-codes param must be comma splitted')


def validate_whitelist(ctx, param, value):
    if not value:
        return []
    try:
        whitelist = value.split(',')
        whitelist = list(map(strip_func, whitelist))
        return whitelist
    except ValueError:
        raise click.BadParameter('--whitelist param must be comma splitted')


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
              callback=validate_allowed_codes, help=('A comma splitted http '
                                                     'response allowed codes'))
@click.option('whitelist', '-w', '--whitelist', type=click.STRING,
              help='A comma splitted whitelist urls',
              callback=validate_whitelist)
def main(doc, timeout, size, debug, allow_codes, whitelist):
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
    request_urls = []
    counts = {}

    for link in links:
        # no static
        if is_static(link):
            continue

        # no dupes
        if link in counts:
            counts[link] += 1
            continue
        else:
            counts[link] = 1

        parsed = urlparse(link)
        # fix no scheme links
        if not parsed.scheme:
            link = 'http://{0}'.format(link)

        # whitelisted
        if whitelist:
            exists = [i for i in whitelist if i in parsed.netloc]
            if len(exists):
                WHITELISTED.append(link)
                continue

        request_urls.append(link)

    counts_keys = counts.keys()
    DUPES.extend([(i, counts[i]) for i in counts_keys if counts[i] > 1])

    requests = (grequests.get(u, timeout=timeout) for u in request_urls)
    responses = grequests.imap(requests, exception_handler=handle_exception,
                               size=size)

    for res in responses:
        status_code = str(res.status_code)
        is_error_code = ERROR_CODE_RE.match(status_code)
        color = 'green'
        if is_error_code:
            if status_code not in allow_codes:
                ERRORS.append((res.status_code, res.url))
                color = 'red'
            else:
                WHITELISTED.append(res.url)

        url = click.style('{0}'.format(res.url), fg='white')
        status = click.style(str(res.status_code), fg=color, bold=True)
        click.secho('- {0} {1}'.format(url, status), fg='green')

    errors_len = len(ERRORS)
    exceptions_len = len(EXCEPTIONS)
    dupes_len = len(DUPES)
    white_len = len(WHITELISTED)

    if errors_len:
        click.echo()
        click.echo('Failed URLs:')
        for code, url in ERRORS:
            code = click.style('{0}'.format(code), bold=True)
            click.secho('- {0} {1}'.format(url, code), fg='red')

    if exceptions_len and debug:
        click.echo()
        import ssl
        click.echo('OpenSSL Version = {0}'.format(ssl.OPENSSL_VERSION))
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
        for url, count in DUPES:
            click.secho('- {0} - {1} times'.format(url, count), fg='yellow',
                        bold=True)

    if white_len and debug:
        click.echo()
        click.echo('Whitelisted (allowed codes and whitelisted param)')
        for url in WHITELISTED:
            click.secho('- {0}'.format(url), fg='magenta')

    click.secho('Total Links Parsed {0}'.format(len(links)), fg='green')
    click.secho('Total Errors {0}'.format(errors_len), fg='red')
    click.secho('Total Exceptions {0}'.format(exceptions_len), fg='red')
    click.secho('Total Dupes {0}'.format(dupes_len), fg='yellow')
    click.secho('Total whitelisted {0}'.format(white_len), fg='yellow')

    if debug:
        click.echo('Execution time: {0:.2f} seconds'.format(time.time() - t1))

    if errors_len:
        sys.exit(1)

if __name__ == "__main__":
    main()
