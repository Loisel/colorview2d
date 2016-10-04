import os
server = 'pypitest'

os.system("python setup.py register -r " + server)
os.system("python setup.py sdist upload -r " + server)

