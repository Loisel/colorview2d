"""Setup module for colorview2d package."""
#!/usr/bin/env python

from setuptools import setup

setup(name='colorview2d',
      version='0.6.1',
      description='2d color plotting tool',
      author='Alois Dirnaichner',
      author_email='alo.dir@gmail.com',
      url='https://github.com/Loisel/colorview2d',
      download_url='https://github.com/Loisel/colorview2d/tarball/v0.6',
      packages=['colorview2d', 'test', 'colorview2d.mods'],
      package_data={'':['default.cv2d'], },
      include_package_data=True,
      install_requires=['pyyaml', 'scikit-image', 'matplotlib', 'numpy'],
      keywords=['plotting', 'colorplot', 'scientific', 'numpy', 'matplotlib'],
      classifiers=[],)
