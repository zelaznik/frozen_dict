from distutils.core import setup

setup(
    name     = 'frozen_dict',
    version  = '1.2',
    url      = 'https://github.com/zelaznik/frozen_dict',

    author       = 'Steve Zelaznik',
    author_email = 'zelaznik@yahoo.com',

    packages = ['frozen_dict'],
    license  = 'MIT License',

    description      = 'An immutable dictionary',
    long_description = open('README.txt').read()
)
