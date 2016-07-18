v(erify)l(inks)
===============


.. image:: https://img.shields.io/pypi/v/vl.svg
   :target: https://pypi.python.org/pypi/vl
.. image:: https://img.shields.io/travis/ellisonleao/vl.svg
   :target: https://travis-ci.org/ellisonleao/vl


A URL link checker CLI command for text files. Heavily inspired on `awesome_bot <https://github.com/dkhamsing/awesome_bot>`_

Installation
------------

Installing pip version:

.. code-block:: shell

    $ pip install vl

Usage
-----

To use it:

.. code-block:: shell

	Usage: vl [OPTIONS] DOC

	  Examples: simple call $ vl README.md

	  Adding debug outputs

	  $ vl README.md --debug

	  Adding a custom timeout for each url. time on seconds.

	  $ vl README.md -t 3

	  Adding a custom size param, to add more requests per time

	  $ vl README -s 1000

	  Skipping some error codes. This will allow 500 and 404 responses to be
	  ignored

	  $ vl README.md -a 500,404

	  Adding Whitelists

	  $ vl README.md -w server1.com,server2.com

	Options:
	  --version               Show the version and exit.
	  -t, --timeout FLOAT     request timeout arg. Default is 2 seconds
	  -s, --size INTEGER      Specifies the number of requests to make at a time.
							  default is 100
	  -d, --debug             Prints out some debug information like execution
							  time and exception messages
	  -a, --allow-codes TEXT  A comma splitted http response allowed codes
	  -w, --whitelist TEXT    A comma splitted whitelist urls
	  --help                  Show this message and exit.


Do i need this lib?
-------------------

I don't know! Currently i am using to check for bad links on my `magictools <https://github.com/ellisonleao/magictools>`_ README file. I hope it can serve for many purposes in the future.


Roadmap
-------

* How can we make it faster?!
* API
