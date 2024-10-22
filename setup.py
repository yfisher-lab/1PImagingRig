import os
from setuptools import setup, find_namespace_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ImagingRig1P",
    version = "0.0.1",
    author = "Mark Plitt",
    author_email = "markplitt@gmail.com",
    description = ("Code for controlling hardware for home built ex vivo imaging rigt"),
    license = "BSD",
    keywords = "",
    url = "https://github.com/yfisher-lab/1PImagingRig.git",
    packages=find_namespace_packages(include=['ImagingRig1P.*']),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
