# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name="v2x-ai-algorithm",
    version="0.1",
    description="",
    author="",
    author_email="",
    test_suite="v2x-ai-algorithm",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=["ez_setup"]),
)
