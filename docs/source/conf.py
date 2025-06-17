import os
import sys
import subprocess

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

def run_apidoc():
    here = os.path.abspath(os.path.dirname(__file__))
    output_path = os.path.join(here)
    module_path = os.path.abspath(os.path.join(here, "../../project/app"))
    subprocess.call(["sphinx-apidoc", "-o", output_path, module_path])

run_apidoc()

project = 'DexQuiz'
copyright = '2025, Lukas Waller'
author = 'Lukas Waller'

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # for Google or NumPy style docstrings
    "sphinx.ext.viewcode",  # (optional) adds links to source code
    "sphinxcontrib.redoc",  # for OpenAPI display
    'sphinxcontrib.plantuml',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

html_sidebars = {
    # For all pages, default sidebar
    '**': ['globaltoc.html', 'relations.html', 'searchbox.html'],

    # For arc42 pages, use minimal sidebar (only local TOC or none)
    'arc42/**': ['searchbox.html'],
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}


sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..', '..', '..', 'project')))
sys.path.insert(0, os.path.abspath('../doc/adr'))
sys.path.insert(0, os.path.abspath('../doc/arc42'))

print("Sphinx sys.path:", sys.path)  # debug print to verify path

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
exclude_patterns = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
