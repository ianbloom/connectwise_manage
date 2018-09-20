#! /usr/bin/python
from setuptools import setup

setup(name='lomo_to_cw',
      version='1.0',
      description='Updates Connectwise Manage with device information from LogicMonitor',
      url='https://github.com/ianbloom/connectwise_manage',
      author='ianbloom',
      author_email='ian.bloom@gmail.com',
      license='MIT',
      packages=['api_helpers'],
      install_requires=[
          'requests',
          'pandas'
      ],
      zip_safe=False)