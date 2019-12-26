#!/usr/bin/env python
'''
EasySettings Setup

@author: Christopher Welborn
'''

from setuptools import setup
defaultdesc = 'Easily set and retrieve application settings.'
try:
    import pypandoc
except ImportError:
    print('Pypandoc not installed, using default description.')
    longdesc = defaultdesc
else:
    # Convert using pypandoc.
    try:
        longdesc = pypandoc.convert('README.md', 'rst')
    except EnvironmentError:
        # Fallback to README.txt (may be behind on updates.)
        try:
            with open('README.txt') as f:
                longdesc = f.read()
        except EnvironmentError:
            print('\nREADME.md and README.txt failed!')
            longdesc = defaultdesc


setup(
    name='EasySettings',
    version='3.2.1',
    author='Christopher Welborn',
    author_email='cj@welbornprod.com',
    packages=['easysettings'],
    url='https://github.com/welbornprod/easysettings',
    license='LICENSE.txt',
    description=open('DESC.txt').read(),
    long_description=longdesc,
    keywords=' '.join((
        'python module library 2 3 settings easy',
        'config setting configuration applications app',
        'json toml yaml pickle ini dict userdict',
    )),
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
