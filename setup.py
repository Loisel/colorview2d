#!/usr/bin/env python

from setuptools import setup

setup(name='colorview2d',
      version='beta0.48',
      description='2d color plotting tool',
      author='Alois Dirnaichner',
      author_email='alo.dir@gmail.com',
      url='https://sourceforge.net/p/colorview2d',
      entry_points={'gui_scripts':[
                    'colorview2d = colorview2d.__main__:main']},
      packages=['colorview2d'],
      package_data={'':['demo.dat','default.cv2d'],},
      include_package_data=True,
      install_requires=['wxPython',
                'matplotlib',
                'scipy',
                'numpy',
                'pyyaml'])

