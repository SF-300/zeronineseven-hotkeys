#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_namespace_packages

setup(name="zeronineseven-hotkeys",
      version="1",
      description="Registry of all the keyboard shortcuts I, zeronineseven, use in everyday live. Also the training programm for htem.",
      author="Vladimir Lebedev",
      author_email="zeronineseven@gmail.com",
      packages=find_namespace_packages(include=["zeronineseven.*"]),
      install_requires=["qasync==0.22.0", "PyQt5==5.15.6", "attr==0.3.1"],
      extras_require={"tests": ["pytest==7.0.0"]},
      )
