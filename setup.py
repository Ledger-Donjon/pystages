#!/usr/bin/python3

from setuptools import setup, find_packages
import sys

setup(
    name="pystages",
    version="1.0",
    # require pyserial
    install_requires=["pyserial", "pyusb", "numpy"],
    packages=find_packages(),
    python_requires=">=3.7",
)
