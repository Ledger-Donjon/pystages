#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='pystages',
    version='1.0',
    install_requires=['pyserial', 'pyusb', 'numpy'],
    packages=find_packages(),
    python_requires='>=3.7')
