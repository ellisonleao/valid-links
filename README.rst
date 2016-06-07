v.l.
====


.. image:: https://img.shields.io/pypi/v/vl.svg
   :target: https://pypi.python.org/pypi/vl
.. image:: https://img.shields.io/travis/ellisonleao/vl.svg
   :target: https://travis-ci.org/ellisonleao/vl

Link validation on text files.


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

.. code-block:: shell

    $ vl README.md --debug
    $ vl README.md -t 10 --size=1000 --debug


Roadmap
-------

* How can we make it faster?!
* Add whitelist param
