import sys
import os

# Add the app directory to the Python path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import fixtures to make them available globally
from .fixtures.sse_fixtures import *
