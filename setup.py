#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

__version__ = '0.4.0'
__author__ = 'Ellison Leão'

dependencies = open('requirements.txt').read().split()
description = open('README.rst').read()

setup(
    name='vl',
    version=__version__,
    url='https://github.com/ellisonleao/vl',
    license='MIT',
    author=__author__,
    author_email='ellisonleao@gmail.com',
    description='A URL link checker CLI command for text files.',
    long_description=description,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'vl = vl.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
