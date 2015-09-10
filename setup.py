#!/usr/bin/env python

from distutils.core import setup

setup(name='OpenSDraw',
      version='0.0.2',
      description='A CAD program similar to OpenSCAD but for LEGO(R).',
      author='Hazen Babcock',
      author_email='hbabcock@mac.com',
      packages=['opensdraw',
                'opensdraw.lcad_language',
                'opensdraw.lcad_lib',
                'opensdraw.library'],
      package_data={'opensdraw':['library/*.lcad',
                                 'examples/*.lcad',
                                 'examples/*.png',
                                 'examples/*.py',
                                 'partviewer/*.py',
                                 'partviewer/*.ui',
                                 'scripts/*.py',
                                 'test/*.lcad',
                                 'test/*.py',
                                 'xml/*.xml']},
      install_requires=['numpy', 'rply', 'scipy']
     )
