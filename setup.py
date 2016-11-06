#!/usr/bin/env python

from setuptools import setup

setup(
    name='livecoin',
    url='https://github.com/metaperl/pylivecoin',
    license='MIT',
    version='0.1.4',
    packages=['livecoin'],
    description='Unofficial Python bindings for the Livecoin API',
    keywords=['livecoin', 'bitcoin', 'exchange'],
    author='Terrence Brannon',
    author_email='metaperl@gmail.com',
    test_suite="livecoin.test.livecoin_test",
    install_requires=["requests==2.7.0"],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Topic :: Office/Business :: Financial',
    ])
