"""Generate a README.txt file from its markdown complement and
register using setup.py
"""
import os
import pandoc

pandoc.core.PANDOC_PATH = '/usr/bin/pandoc'
server = 'pypitest'

doc = pandoc.Document()
doc.markdown = open('README.md').read()
with open('README.txt', 'w+') as readme:
    readme.write(doc.rst)

os.system("python setup.py register -r " + server)
os.system("python setup.py sdist upload -r " + server)
os.remove('README.txt')
