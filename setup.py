#!/usr/bin/env python

from distutils.core import setup

setup(name='OpenSDraw',
      version='0.0.2',
      description='A CAD program similar to OpenSCAD but for LEGO(R).',
      author='Hazen Babcock',
      author_email='hbabcock@mac.com',
      packages=['opensdraw'],
      install_requires['numpy', 'rply', 'scipy']
     )
