import os
import sys
sys.path.insert(0, os.path.abspath('project/app'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google-style docstrings
    'sphinx.ext.viewcode',  # For viewing source code in docs
]