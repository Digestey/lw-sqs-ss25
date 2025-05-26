import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DexQuiz'
copyright = '2025, Lukas Waller'
author = 'Lukas Waller'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]


sys.path.insert(0, os.path.abspath('../project/app'))
sys.path.insert(0, os.path.abspath('../doc/adr'))
sys.path.insert(0, os.path.abspath('../doc/arc42'))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
