import sys

path = '/projects/lf'

sys.path.insert(0, path)
from app import app as application
