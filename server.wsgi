import sys

path = '/projects/lf'

activate_this = path + '/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, path)
from app import app as application
