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
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # for Google or NumPy style docstrings
    "sphinx.ext.viewcode", 
    "sphinxcontrib.redoc",  # for OpenAPI display
    "sphinxcontrib.openapi"
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


html_theme = "furo"

html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}


sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..', '..', '..', 'project')))
sys.path.insert(0, os.path.abspath(os.path.join(__file__, 'arc42', 'images')))


print("Sphinx sys.path:", sys.path)  # debug print to verify path

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
