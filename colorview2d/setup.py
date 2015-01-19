#!/usr/bin/env python

from distutils.core import setup

setup(name='colorview2d',
      version='0.4',
      description='2d color plotting tool',
      author='Alois Dirnaichner',
      author_email='alo.dir@gmail.com',
      url='https://gitorious.org/colorview2d',
      scripts=['colorview2d.py'],
      py_modules=['LinecutFrame','LineoutFrame','MainFrame','MyLine','PlotFrame','SlopeExFrame','Subject','View','CropFrame','LabelticksFrame','FloatValidator','gpfile','floatslider','floatspin','toolbox'],
      data_files=[('data',['demo.dat']),('config',['default.config'])],
      requires=['wx',
                'matplotlib',
                'scipy',
                'numpy',
                'yaml'])

