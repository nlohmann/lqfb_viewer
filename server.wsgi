import sys

path = '/projects/lf'

sys.path.insert(0, path)
from server import app as application
