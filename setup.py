#!/usr/bin/env python3
import os

from setuptools import setup

with open('README.md', 'r') as r:
    readme = r.read()

version = os.environ.get('GGW_VERSION', '0.0.0')

download_url = (
    'https://github.com/jkeifer/GRACE/tarball/%s'
)


setup(
    name='py-ggw',
    packages=['py_ggw'],
    version=version,
    description='Process GRACE gravity anomoly data to view groundwater usage over time.',
    long_description=readme,
    author='Jarrett Keifer',
    author_email='jkeifer0@gmail.com',
    url='https://github.com/jkeifer/GRACE',
    download_url=download_url % version,
    entry_points='''
        [console_scripts]
        ggw=py_ggw.cli:main
    ''',
    install_requires=(
        'geoplot',
        'rioxarray',
        'cftime',
        'imageio',
    ),
)
