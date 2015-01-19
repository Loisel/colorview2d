#!/usr/bin/env python

from distutils.core import setup

setup(name='colorview2d',
      version='beta0.4',
      description='2d color plotting tool',
      author='Alois Dirnaichner',
      author_email='alo.dir@gmail.com',
      url='https://sourceforge.net/p/colorview2d',
      scripts=['colorview2d.py'],
      packages=['colorview2d'],
      data_files=[('data',['demo.dat']),('config',['default.config'])],
      requires=['wx',
                'matplotlib',
                'scipy',
                'numpy',
                'yaml'])

