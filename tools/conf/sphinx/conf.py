# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Configuration file for the Sphinx documentation builder.
#
# For a full list see the documentation:
# [SPHINX_CONF](https://www.sphinx-doc.org/en/master/usage/configuration.html)


# Imports
# =======

import pathlib
import sphinx.application
import sys
import typing

# Path management.
_root_scenario_path = pathlib.Path(__file__).parents[3]  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "tools" / "src"))


# Project information
# ===================

# [SPHINX_CONF]: "The documented project's name."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-project
project = "scenario"  # type: str

# [SPHINX_CONF]: "The author name(s) of the document."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-author
author = "Alexis Royer <alexis.royer@gmail.com>"  # type: str

# [SPHINX_CONF]: "A copyright statement in the style '2008, Author Name'."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-copyright
copyright = "2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>"  # type: str  # noqa  ## Shadows built-in name 'copyright'

# [SPHINX_CONF]: "The major project version, used as the replacement for |version|.
#                 For example, for the Python documentation, this may be something like 2.6."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-version
version = "0.2.2"  # type: str


# General configuration
# =====================
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# [SPHINX_CONF]: "A list of strings that are module names of extensions.
#                 These can be extensions coming with Sphinx (named sphinx.ext.*) or custom ones."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-extensions
#
# Will be extended later in this script.
extensions = []  # type: typing.List[str]

# [SPHINX_CONF]: "If true, the reST sources are included in the HTML build as ``_sources/name``. The default is ``True``."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_copy_source
html_copy_source = False  # type: bool

# [SPHINX_CONF]: "A list of glob-style patterns that should be excluded when looking for source files.
#                 They are matched against the source file names relative to the source directory, using slashes as directory separators on all platforms."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns
exclude_patterns = [
    # The `modules.rst` output file is of little value.
    # The `scenario.rst` file is referenced directly.
    "py/modules.rst",
]  # type: typing.List[str]

# [SPHINX_CONF]: "A boolean that decides whether module names are prepended to all object names (for object types where a “module” of some kind is defined),
#                 e.g. for py:function directives. Default is True."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-add_module_names
#
# Inspired from https://stackoverflow.com/questions/20864406/remove-package-and-module-name-from-sphinx-function
add_module_names = False  # type: bool


# Options for internationalization
# ================================
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-internationalization


# Options for Math
# ================
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-math


# Options for HTML output
# =======================
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# [SPINX_DOC]: "The "theme" that the HTML output should use. See the section about theming.
#               The default is 'alabaster'."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_theme
# See https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes
# Define no template. Let the default template take place on https://readthedocs.org/.
# html_theme = "bizstyle"  # type: str
# html_theme = "pyramid"  # type: str  # Warning: Does not display admonition titles.

# [SPHINX_CONF]: "A dictionary of options that influence the look and feel of the selected theme.
#                 These are theme-specific."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_theme_options
html_theme_options = {
    # Inspired from https://stackoverflow.com/questions/23211695/modifying-content-width-of-the-sphinx-theme-read-the-docs#54379799
    "body_max_width": "80%",
}  # type: typing.Dict[str, str]


# TODOs
# =====
# See [SPHINX_TODO] https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

extensions.append("sphinx.ext.todo")

# [SPHINX_TODO]: "If this is True, todo and todolist produce output, else they produce nothing."
# See https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#confval-todo_include_todos
todo_include_todos = True  # type: bool

# [SPHINX_TODO]: "If this is True, todo emits a warning for each TODO entries."
# See https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#confval-todo_emit_warnings
todo_emit_warnings = True  # type: bool


# Graphs
# ======
# See https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html

# No need to use the ``sphinx.ext.graphviz`` extension in as much as PlantUML is used directly to generate the diagrams.
# extensions.append("sphinx.ext.graphviz")


# Sphinx augmentation
# ===================

# Make `scenario.tools.sphinx.setup()` be called automatically by Sphinx.
import scenario.tools.sphinx  # noqa  ## Module level import not at top of file
setup = scenario.tools.sphinx.setup  # type: typing.Callable[[sphinx.application.Sphinx], None]


# Python documentation
# ====================

# Auto-document python files.
# See [SPHINX_AUTODOC] https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# `sphinx-apidoc` generates .rst files, in the `py` directory, with `.. automodule` directives that the `autodoc` extension processes.
extensions.append("sphinx.ext.autodoc")

# Autodoc needs the path to be set appropriately so that the Python modules can be loaded and inspected.
sys.path.insert(0, str(_root_scenario_path / "src"))

# [SPHINX_AUTODOC]: "This value selects what content will be inserted into the main body of an autoclass directive. (...)
#                    "class" Only the class’ docstring is inserted. This is the default.
#                    You can still document __init__ as a separate method using automethod or the members option to autoclass."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autoclass_content
autoclass_content = "class"  # type: str

# [SPHINX_AUTODOC]: "This value selects if automatically documented members are sorted alphabetical (value 'alphabetical'),
#                    by member type (value 'groupwise') or by source order (value 'bysource').
#                    The default is alphabetical."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_member_order
autodoc_member_order = "bysource"  # type: str

# [SPHINX_AUTODOC]: "The default options for autodoc directives.
#                    They are applied to all autodoc directives automatically.
#                    It must be a dictionary which maps option names to the values.
#                    (...)
#                    The supported options are 'members', 'member-order', 'undoc-members', 'private-members', 'special-members', 'inherited-members',
#                    'show-inheritance', 'ignore-module-all', 'imported-members', 'exclude-members', 'class-doc-from' and 'no-value'."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
#
# Probably useless when the `SPHINX_APIDOC_OPTIONS` environment variable is set when executing `sphinx-apidoc`,
# in as much as this configuration describes *default behaviours* when nothing already specified.
autodoc_default_options = {
}  # type: typing.Dict[str, typing.Any]

# [SPHINX_AUTODOC]: "If this boolean value is set to True (which is the default), autodoc will look at the first line of the docstring
#                    for functions and methods, and if it looks like a signature, use the line as the signature
#                    and remove it from the docstring content."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_docstring_signature
autodoc_docstring_signature = False  # type: bool

# [SPHINX_AUTODOC]: "This value controls how to represent typehints. The setting takes the following values:
#                    - 'signature' - Show typehints in the signature (default)
#                    - 'description' - Show typehints as content of the function or method.
#                      The typehints of overloaded functions or methods will still be represented in the signature.
#                    - 'none' - Do not show typehints
#                    - 'both' - Show typehints in the signature and as content of the function or method
#
#                    Overloaded functions or methods will not have typehints included in the description
#                    because it is impossible to accurately represent all possible overloads as a list of parameters."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_typehints
#
# Memo: The 'signature' configuration does not activate typehints on readthedocs...
autodoc_typehints = "description"

# [SPHINX_AUTODOC]: "A dictionary for users defined type aliases that maps a type name to the full-qualified object name.
#                    It is used to keep type aliases not evaluated in the document. Defaults to empty ({})."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_type_aliases
autodoc_type_aliases = {
    # Fed by `scenario.tools.sphinx`.
}  # type: typing.Dict[str, str]

# [SPHINX_AUTODOC]: "This value controls the format of typehints. The setting takes the following values:
#                    - 'fully-qualified' - Show the module name and its name of typehints
#                    - 'short' - Suppress the leading module names of the typehints (ex. `io.StringIO` -> `StringIO`) (default)
#
#                    Changed in version 5.0: The default setting was changed to 'short'"
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_typehints_format
autodoc_typehints_format = "fully-qualified"  # type: str

# [SPHINX_AUTODOC]: "This value controls the behavior of sphinx-build -W during importing modules.
#                    If False is given, autodoc forcedly suppresses the error if the imported module emits warnings."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_warningiserror
autodoc_warningiserror = True  # type: bool

# [SPHINX_AUTODOC]: "This value controls the docstrings inheritance.
#                    If set to True the docstring for classes or methods, if not explicitly set, is inherited from parents."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_inherit_docstrings
autodoc_inherit_docstrings = True  # type: bool
