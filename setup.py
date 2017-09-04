#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='OpenSDraw',
      version='0.0.2',
      description='A CAD program similar to OpenSCAD but for LEGO(R).',
      author='Hazen Babcock',
      author_email='hbabcock@mac.com',

      packages = find_packages(),

      package_data={},
      exclude_package_data={},
      include_package_data=True,
      
      requires=[],
      
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
)
