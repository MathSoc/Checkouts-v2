import os
from setuptools import setup

def load_requirements():
    """
    Loads the requirements from the the requirements file into an array.

    :return [string]
    """
    reqfile = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    return open(reqfile).read().splitlines()

setup(
    name='checkouts',
    version='0.0.1',
    author='Ford Peprah',
    author_email='ford.peprah@uwaterloo.ca',
    url='http://www.github.com/mathsoc/checkouts-v2',
    packages=['checkouts'],
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements()
)
