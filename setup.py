#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

    setup(
        name='fixedwidthtext',
        author=u'André Ferreira',
        author_email='lopinho@gmail.com',
        description='Library to extract data from semi-structured text documents',
        long_description=long_description,
        license='MIT',
        url="http://github.org/lopinho/fixedwidthtext",
        version='0.1',
        packages=['fixedwidthtext'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
