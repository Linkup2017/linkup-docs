# -- Project information -------------------------------------------------------
project = "Linkup Infotech Docs"
copyright = "2026, Linkup Infotech Co., Ltd."
author = "Linkup Infotech Team"
release = "1.0.0"

# -- General configuration -----------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_tabs.tabs",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Language / i18n -----------------------------------------------------------
language = "en"
locale_dirs = ["locale/"]
gettext_compact = False

# -- MyST Parser ---------------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "fieldlist",
    "substitution",
]
myst_heading_anchors = 3
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- HTML output ---------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
# html_logo = "_static/img/logo.svg"      # TODO: add Linkup Infotech logo
# html_favicon = "_static/img/favicon.ico"  # TODO: add favicon

html_theme_options = {
    "logo_only": True,
    "navigation_depth": 3,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
    # "display_version": True,  # removed: unsupported in sphinx-rtd-theme 3.x
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
}

html_context = {
    "display_github": True,
    "github_user": "linkup-co-kr",
    "github_repo": "linkup-docs",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Mermaid -------------------------------------------------------------------
mermaid_version = "11"

# -- Copybutton ----------------------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
