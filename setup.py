#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="colony",
    version="0.1",
    description="Colony simulator.",
    author="Mizaimao",
    packages=find_packages(include=["colony", "colony.*"]),
)
