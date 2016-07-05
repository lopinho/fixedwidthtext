#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
            tox.cmdline(args=args)

with open('README.rst') as f:
    long_description = f.read()

    setup(
        tests_require=['tox'],
        cmdclass={'test': Tox},
        name='fixedwidthtext',
        author=u'André Ferreira',
        author_email='lopinho@gmail.com',
        description='Library to extract data from semi-structured text documents',
        long_description=long_description,
        license='MIT',
        url="http://github.org/lopinho/fixedwidthtext",
        version='0.1.2',
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
        install_requires=[
            'six'
        ]
    )
