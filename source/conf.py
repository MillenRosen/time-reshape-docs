"""Public user guide; builds independently of the application and its services."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent
release_data = json.loads((ROOT / "_data/release.json").read_text(encoding="utf-8"))
project = "时光重塑"
author = "时光重塑项目组"
copyright = "2026, 时光重塑项目组"
version = release = release_data["version"]
language = "zh_CN"
extensions = ["myst_parser"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_includes/**"]
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3
nitpicky = True
html_theme = "sphinx_rtd_theme"
html_title = "时光重塑 · 使用手册"
html_short_title = "时光重塑"
html_logo = "_static/images/brand-mark.webp"
html_favicon = "_static/images/favicon.svg"
html_static_path = ["_static"]
html_css_files = ["guide.css"]
html_js_files = [("guide.js", {"defer": "defer"})]
templates_path = ["_templates"]
html_show_sourcelink = False
html_show_sphinx = False
html_last_updated_fmt = None
html_theme_options = {
    "logo_only": False,
    "version_selector": False,
    "language_selector": False,
    "collapse_navigation": False,
    "navigation_depth": 2,
    "prev_next_buttons_location": "bottom",
    "style_nav_header_background": "#eef3e9",
}
html_context = {"guide_release": release_data}
if os.environ.get("READTHEDOCS_CANONICAL_URL"):
    html_baseurl = os.environ["READTHEDOCS_CANONICAL_URL"]


def apply_release_data(app, docname, source):
    # Expand before Markdown parsing so URLs and inline code work too.
    # Only known public metadata is substituted; no template evaluation.
    for key, value in release_data.items():
        source[0] = source[0].replace("{{ " + key + " }}", str(value))


def setup(app):
    app.connect("source-read", apply_release_data)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
