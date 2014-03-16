#!/usr/bin/env python
'''
EasySettings Setup

@author: Christopher Welborn
'''

from distutils.core import setup

setup(
    name='EasySettings',
    version='1.8.9',
    author='Christopher Welborn',
    author_email='cj@welbornprod.com',
    packages=['easysettings'],
    url='http://pypi.python.org/pypi/EasySettings/',
    license='LICENSE.txt',
    description=open('DESC.txt').read(),
    long_description=open('README.txt').read(),
    keywords=('python module library 2 3 settings easy '
              'config setting configuration applications app'),
    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
