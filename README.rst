==
vl
==

.. image:: https://img.shields.io/pypi/v/valid_links.svg
   :target: https://pypi.python.org/pypi/valid_links
.. image:: https://img.shields.io/travis/ellisonleao/valid_links.svg
   :target: https://travis-ci.org/ellisonleao/valid_links

Link validation on text files.


Installation
------------

Installing pip version:

	$ pip install valid_links

Usage
-----

To use it:

    Usage: vl [OPTIONS] DOC

	  Main CLI method

	Options:
	  -t, --timeout FLOAT  request timeout arg. Default is 2 seconds
	  -s, --size INTEGER   Specifies the number of requests to make at a time.
						   default is 100
	  -d, --debug          Prints out some debug information like execution time
						   and exception messages
	  --help               Show this message and exit


Examples
--------

	$ vl README.md --debug
	$ vl README.md -t 10 --size=1000 --debug


Roadmap
-------

* How can we make it faster?!
* Add whitelist param
