# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "api"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="Now Playing API",
    author_email="jeremiejost@gmail.com",
    url="",
    keywords=["Swagger", "Now Playing API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['api=api.__main__:main']},
    long_description="""\
    Now Playing API.
    """
)

