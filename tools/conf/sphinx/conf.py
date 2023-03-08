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

import docutils.nodes
import enum
import inspect
import logging
import pathlib
import re
import sphinx.application
import sphinx.ext.autodoc
import sys
import types
import typing

MAIN_PATH = pathlib.Path(__file__).parents[3]  # type: pathlib.Path
sys.path.append(str(MAIN_PATH / "src"))
sys.path.append(str(MAIN_PATH / "tools" / "src"))
import scenario  # noqa: E402  ## Module level import not at top of file
import scenario.tools  # noqa: E402  ## Module level import not at top of file


# Project information
# ===================

# [SPHINX_CONF]: "The documented project's name."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-project
project = "scenario"

# [SPHINX_CONF]: "The author name(s) of the document."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-author
author = "Alexis Royer <alexis.royer@gmail.com>"

# [SPHINX_CONF]: "A copyright statement in the style '2008, Author Name'."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-copyright
copyright = "2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>"  # noqa  ## Shadows built-in name 'copyright'

# [SPHINX_CONF]: "The major project version, used as the replacement for |version|.
#                 For example, for the Python documentation, this may be something like 2.6."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-version
version = "0.2.2"


# General configuration
# =====================
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# [SPHINX_CONF]: "A list of strings that are module names of extensions.
#                 These can be extensions coming with Sphinx (named sphinx.ext.*) or custom ones."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-extensions
extensions = []  # Will be extended later in this script.

# [SPHINX_CONF]: "If true, the reST sources are included in the HTML build as ``_sources/name``. The default is ``True``."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_copy_source
html_copy_source = False

# [SPHINX_CONF]: "A list of glob-style patterns that should be excluded when looking for source files.
#                 They are matched against the source file names relative to the source directory, using slashes as directory separators on all platforms."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns
exclude_patterns = [
    # The `modules.rst` output file is of little value.
    # The `scenario.rst` file is referenced directly.
    "py/modules.rst",
]

# [SPHINX_CONF]: "A boolean that decides whether module names are prepended to all object names (for object types where a “module” of some kind is defined),
#                 e.g. for py:function directives. Default is True."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-add_module_names
add_module_names = False  # Inspired from https://stackoverflow.com/questions/20864406/remove-package-and-module-name-from-sphinx-function


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
# html_theme = "bizstyle"
# html_theme = "pyramid"  # Warning: Does not display admonition titles.

# [SPHINX_CONF]: "A dictionary of options that influence the look and feel of the selected theme.
#                 These are theme-specific."
# See https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_theme_options
html_theme_options = {
    # Inspired from https://stackoverflow.com/questions/23211695/modifying-content-width-of-the-sphinx-theme-read-the-docs#54379799
    "body_max_width": "80%",
}


# TODOs
# =====
# See [SPHINX_TODO] https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

TODO_EXT = True
if TODO_EXT:
    extensions.append("sphinx.ext.todo")

    # [SPHINX_TODO]: "If this is True, todo and todolist produce output, else they produce nothing."
    # See https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#confval-todo_include_todos
    todo_include_todos = True

    # [SPHINX_TODO]: "If this is True, todo emits a warning for each TODO entries."
    # See https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#confval-todo_emit_warnings
    todo_emit_warnings = True


# Graphs
# ======
# See https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html

# No need to use the ``sphinx.ext.graphviz`` extension in as much as PlantUML is used directly to generate the diagrams.
# extensions.append("sphinx.ext.graphviz")


# Sphinx augmentation
# ===================

def setup(
        app,  # type: sphinx.application.Sphinx
):  # type: (...) -> None
    """
    This function will be called automatically by the Sphinx application.

    :param app: Sphinx application.
    """
    _pydoc = PyDoc()
    _pydoc.setup(app)


# Logging
# =======

# In order to have sphinx display debugging information, use `tools/sphinx.sh -vv`.
# The `-vv` option is passed on the *shpinx-build* command.

def sphinxlogger():  # type: (...) -> logging.Logger
    return logging.getLogger("sphinx")


def sphinxdebug(
        fmt,  # type: str
        *args  # type: typing.Any
):  # type: (...) -> None
    sphinxlogger().debug(f"[conf] {fmt}", *args)


def sphinxinfo(
        msg,  # type: str
):  # type: (...) -> None
    sphinxlogger().debug("[conf] INFO: %s", msg)
    sphinxlogger().info(msg)


def sphinxwarning(
        msg,  # type: str
):  # type: (...) -> None
    sphinxlogger().debug("[conf] WARNING: %s", msg)
    sphinxlogger().warning(f"WARNING: {msg}")


# Python documentation
# ====================

# Auto-document python files.
# See [SPHINX_AUTODOC] https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# `sphinx-apidoc` generates .rst files, in the `py` directory, with `.. automodule` directives that the `autodoc` extension processes.
extensions.append("sphinx.ext.autodoc")

# Autodoc needs the path to be set appropriately so that the Python modules can be loaded and inspected.
sys.path.insert(0, str(MAIN_PATH / "src"))

# [SPHINX_AUTODOC]: "This value selects what content will be inserted into the main body of an autoclass directive. (...)
#                    "class" Only the class’ docstring is inserted. This is the default.
#                    You can still document __init__ as a separate method using automethod or the members option to autoclass."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autoclass_content
autoclass_content = "class"

# [SPHINX_AUTODOC]: "This value selects if automatically documented members are sorted alphabetical (value 'alphabetical'),
#                    by member type (value 'groupwise') or by source order (value 'bysource').
#                    The default is alphabetical."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_member_order
autodoc_member_order = "bysource"

# [SPHINX_AUTODOC]: "If this boolean value is set to True (which is the default), autodoc will look at the first line of the docstring
#                    for functions and methods, and if it looks like a signature, use the line as the signature
#                    and remove it from the docstring content."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_docstring_signature
autodoc_docstring_signature = False

# [SPHINX_AUTODOC]: "This value controls the behavior of sphinx-build -W during importing modules.
#                    If False is given, autodoc forcedly suppresses the error if the imported module emits warnings."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_warningiserror
autodoc_warningiserror = True

# [SPHINX_AUTODOC]: "This value controls the docstrings inheritance.
#                    If set to True the docstring for classes or methods, if not explicitly set, is inherited from parents."
# See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_inherit_docstrings
autodoc_inherit_docstrings = True


class PyDoc:

    WARN_IN_DOC = False  # type: bool

    class DocumentedItem:
        def __init__(
                self,
                obj_type,  # type: str
                obj,  # type: object
                lines,  # type: typing.List[str]
        ):  # type: (...) -> None
            self.type = obj_type  # type: str
            self.obj = obj  # type: object
            self.lines = lines  # type: typing.List[str]

    def __init__(self):  # type: (...) -> None
        self._documented_items = {}  # type: typing.Dict[str, PyDoc.DocumentedItem]
        #: Dictionary of {fully qualified name: type of object}.
        self._tracked_items = {}  # type: typing.Dict[str, str]

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        # ``sphinx`` events:
        # ==================

        # See [SPHINX_CORE_EVENTS] https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
        # for an overview of events that happen during a build.
        #
        # 1. event.config-inited(app,config)
        app.connect("config-inited", self.sphinx_configinited)

        # 2. event.builder-inited(app)
        app.connect("builder-inited", self.sphinx_builderinited)

        # 3. event.env-get-outdated(app, env, added, changed, removed)
        # 4. event.env-before-read-docs(app, env, docnames)
        #
        # for docname in docnames:
        #    5. event.env-purge-doc(app, env, docname)
        #
        #    if doc changed and not removed:
        #       6. source-read(app, docname, source)
        #       7. run source parsers: text -> docutils.document
        #          - parsers can be added with the app.add_source_parser() API
        #       8. apply transforms based on priority: docutils.document -> docutils.document
        #          - event.doctree-read(app, doctree) is called in the middle of transforms,
        #            transforms come before/after this event depending on their priority.
        #
        # 9. event.env-merge-info(app, env, docnames, other)
        #    - if running in parallel mode, this event will be emitted for each process
        #
        # 10. event.env-updated(app, env)
        app.connect("env-updated", self.sphinx_envupdated)
        # 11. event.env-get-updated(app, env)
        # 12. event.env-check-consistency(app, env)
        #
        # # The updated-docs list can be builder dependent, but generally includes all new/changed documents,
        # # plus any output from `env-get-updated`, and then all "parent" documents in the ToC tree
        # # For builders that output a single page, they are first joined into a single doctree before post-transforms
        # # or the doctree-resolved event is emitted
        # for docname in updated-docs:
        #    13. apply post-transforms (by priority): docutils.document -> docutils.document
        #    14. event.doctree-resolved(app, doctree, docname)
        #        - In the event that any reference nodes fail to resolve, the following may emit:
        #        - event.missing-reference(env, node, contnode)
        #        - event.warn-missing-reference(domain, node)
        app.connect("doctree-resolved", self.sphinx_doctreeresolved)
        #
        # 15. Generate output files
        # 16. event.build-finished(app, exception)
        app.connect("build-finished", self.sphinx_buildfinished)

        # ``autodoc`` events.
        # ===================

        # See [SPHINX_AUTODOC_EVENTS]:
        # - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#docstring-preprocessing
        # - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#skipping-members
        app.connect("autodoc-skip-member", self.autodoc_skipmember)
        # Hack *autodoc* so that it does not display attribute values (see [sphinx#904](https://github.com/sphinx-doc/sphinx/issues/904)).
        sphinx.ext.autodoc.object_description = self.autodoc_objectdescription
        app.connect("autodoc-process-signature", self.autodoc_processsignature)
        app.connect("autodoc-process-docstring", self.autodoc_processdocstring)

    def sphinx_configinited(
            self,
            app,  # type: sphinx.application.Sphinx
            config,  # type: sphinx.application.Config
    ):  # type: (...) -> None
        """
        https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-config-inited

        [SPHINX_CORE_EVENTS]:
            config-inited(app, config)

            Emitted when the config object has been initialized.
        """
        sphinxdebug("PyDoc.sphinx_configinited()")

        sphinxdebug("app.confdir=%r", app.confdir)
        sphinxdebug("app.doctreedir=%r", app.doctreedir)
        sphinxdebug("app.outdir=%r", app.outdir)
        sphinxdebug("app.srcdir=%r", app.srcdir)

        # Fix 'doc/src' path if needed.
        if pathlib.Path(app.srcdir) != scenario.tools.paths.DOC_SRC_PATH:
            sphinxinfo(f"Fixing source directory from {app.srcdir!r} to {scenario.tools.paths.DOC_SRC_PATH.abspath!r}")
            app.srcdir = scenario.tools.paths.DOC_SRC_PATH.abspath

        # Update 'doc/src/py' files.
        scenario.tools.MkDoc().sphinxapidoc()

    def sphinx_builderinited(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-builder-inited

        [SPHINX_CORE_EVENTS]:
            builder-inited(app)

            Emitted when the builder object has been created.
            It is available as ``app.builder``.
        """
        sphinxdebug("PyDoc.sphinx_builderinited()")

    def sphinx_envupdated(
            self,
            app,  # type: sphinx.application.Sphinx
            env,  # type: typing.Any
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-env-updated

        [SPHINX_CORE_EVENTS]:
            env-updated(app, env)

            Emitted when the update() method of the build environment has completed, that is, the environment and all doctrees are now up-to-date.

            You can return an iterable of docnames from the handler. These documents will then be considered updated,
            and will be (re-)written during the writing phase.
        """
        sphinxdebug("PyDoc.sphinx_envupdated(env=%r)", env)

        self._warnundocitems()

    def sphinx_doctreeresolved(
            self,
            app,  # type: sphinx.application.Sphinx
            doctree,  # type: docutils.nodes.document
            docname,  # type: str
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-doctree-resolved

        [SPHINX_CORE_EVENTS]:
            doctree-resolved(app, doctree, docname)

            Emitted when a doctree has been “resolved” by the environment,
            that is, all references have been resolved and TOCs have been inserted.
            The doctree can be modified in place.

            Here is the place to replace custom nodes that don’t have visitor methods in the writers,
            so that they don’t cause errors when the writers encounter them.
        """
        sphinxdebug("PyDoc.sphinx_doctreeresolved(doctree=%r, docname=%r)", doctree, docname)
        self._simplifyreferences(docname, doctree)

    def sphinx_buildfinished(
            self,
            app,  # type: sphinx.application.Sphinx
            exception,  # type: typing.Optional[Exception]
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-build-finished

        [SPHINX_CORE_EVENTS]:
            build-finished(app, exception)

            Emitted when a build has finished, before Sphinx exits, usually used for cleanup.
            This event is emitted even when the build process raised an exception, given as the exception argument.
            The exception is reraised in the application after the event handlers have run.
            If the build process raised no exception, exception will be None.
            This allows to customize cleanup actions depending on the exception status.
        """
        sphinxdebug("PyDoc.sphinx_buildfinished(exception=%r)", exception)

    def autodoc_skipmember(
            self,
            app,  # type: sphinx.application.Sphinx
            owner_type,  # type: str
            nfq_name,  # type: str
            obj,  # type: typing.Optional[object]
            would_skip,  # type: bool
            options,  # type: typing.Any
    ):  # type: (...) -> typing.Optional[bool]
        """
        See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-skip-member

        [SPHINX_AUTODOC_EVENTS]:
            autodoc-skip-member(app, what, name, obj, skip, options)

            Emitted when autodoc has to decide whether a member should be included in the documentation.
            The member is excluded if a handler returns True. It is included if the handler returns False.

            If more than one enabled extension handles the autodoc-skip-member event, autodoc will use the first non-None value returned by a handler.
            Handlers should return None to fall back to the skipping behavior of autodoc and other enabled extensions.

        :param app:
            [SPHINX_AUTODOC_EVENTS]:
                The Sphinx application object
        :param owner_type:
            ``what`` in [SPHINX_AUTODOC_EVENTS]

            [SPHINX_AUTODOC_EVENTS]:
                The type of the object which the docstring belongs to
                (one of "module", "class", "exception", "function", "method", "attribute")"

            .. warning:: Actually the type of the owner object! (see `sphinx#6808 <https://github.com/sphinx-doc/sphinx/issues/6808>`_)
        :param nfq_name:
            ``name`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                The fully qualified name of the object

            .. warning:: Actually not a fully qualified name. (see `sphinx#6808 <https://github.com/sphinx-doc/sphinx/issues/6808>`_)
        :param obj:
            [SPHINX_AUTODOC_EVENTS]:
                The object itself

            .. warning:: May be None, especially for class attributes.
            .. note:: Equal to :attr:`sphinx.ext.autodoc.INSTANCEATTR` for instance attributes.
        :param would_skip:
            ``skip`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                A boolean indicating if autodoc will skip this member if the user handler does not override the decision
        :param options:
            [SPHINX_AUTODOC_EVENTS]:
                The options given to the directive:
                an object with attributes inherited_members, undoc_members, show_inheritance and noindex
                that are true if the flag option of same name was given to the auto directive
        :return:
            [SPHINX_AUTODOC_EVENTS]:
                The member is excluded if a handler returns True. It is included if the handler returns False.
                If more than one enabled extension handles the autodoc-skip-member event,
                autodoc will use the first non-None value returned by a handler.
                Handlers should return None to fall back to the skipping behavior of autodoc and other enabled extensions.

        Prevents ``__init__()``, ``__repr__()`` and ``__str__()`` methods from being skipped.
        """
        sphinxdebug("PyDoc.autodoc_skipmember(owner_type=%r, nfq_name=%r, obj=%r, would_skip=%r, options=%r)",
                    owner_type, nfq_name, obj, would_skip, options)

        if would_skip:
            # When overriding `enum.Enum`, an undocumented function warning is displayed for '_generate_next_value_'.
            # noinspection PyProtectedMember
            if obj == enum.Enum._generate_next_value_:
                sphinxdebug("PyDoc.autodoc_skipmember(): `%s` should be skipped!", self._fqname(obj))
                return True

            if inspect.isclass(obj) and (nfq_name != "__metaclass__"):
                sphinxdebug("PyDoc.autodoc_skipmember(): class `%s` not skipped!", self._fqname(obj))
                return False
            if inspect.isfunction(obj):
                sphinxdebug("PyDoc.autodoc_skipmember(): function `%s` not skipped!", self._fqname(obj))
                return False
            if inspect.ismethod(obj):
                sphinxdebug("PyDoc.autodoc_skipmember(): method `%s` not skipped!", self._fqname(obj))
                return False
            if owner_type in ("class", "exception"):
                if obj is not None:
                    if self._isspecialfunction(obj):
                        sphinxdebug("PyDoc.autodoc_skipmember(): method `%s` not skipped!", self._fqname(obj))
                        return False
                    if obj is sphinx.ext.autodoc.INSTANCEATTR:
                        sphinxdebug("PyDoc.autodoc_skipmember(): instance attribute `%s` not skipped!", nfq_name)
                        return False
                    if not nfq_name.startswith("__"):
                        sphinxdebug("PyDoc.autodoc_skipmember(): instance attribute `%s` not skipped!", nfq_name)
                        return False
                else:
                    if not nfq_name.startswith("__"):
                        sphinxdebug("PyDoc.autodoc_skipmember(): class attribute `%s` not skipped!", nfq_name)
                        return False

        sphinxdebug("PyDoc.autodoc_skipmember(nfq_name=%r) => default would_skip=%r", nfq_name, would_skip)
        return None

    def autodoc_processsignature(
            self,
            app,  # type: sphinx.application.Sphinx
            what,  # type: str
            fq_name,  # type: str
            obj,  # type: typing.Optional[object]
            options,  # type: typing.Any
            signature,  # type: typing.Optional[str]
            return_annotation,  # type: typing.Optional[str]
    ):  # type: (...) -> typing.Optional[typing.Tuple[typing.Optional[str], typing.Optional[str]]]
        """
        See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-process-signature

        [SPHINX_AUTODOC_EVENTS]:
            autodoc-process-signature(app, what, name, obj, options, signature, return_annotation)

            Emitted when autodoc has formatted a signature for an object.

        :param app:
            [SPHINX_AUTODOC_EVENTS]:
                The Sphinx application object
        :param what:
            [SPHINX_AUTODOC_EVENTS]:
                The type of the object which the docstring belongs to
                (one of "module", "class", "exception", "function", "method", "attribute")

            .. note:: Actually is the type of the current object, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param fq_name:
            ``name`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                The fully qualified name of the object

            .. note:: Actually is the fully qualified name, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param obj:
            [SPHINX_AUTODOC_EVENTS]:
                The object itself

            .. warning:: May be None, especially for attributes.
        :param options:
            [SPHINX_AUTODOC_EVENTS]:
                The options given to the directive:
                an object with attributes inherited_members, undoc_members, show_inheritance and noindex
                that are true if the flag option of same name was given to the auto directive
        :param signature:
            [SPHINX_AUTODOC_EVENTS]:
                Function signature, as a string of the form "(parameter_1, parameter_2)",
                or None if introspection didn't succeed and signature wasn't specified in the directive.
        :param return_annotation:
            [SPHINX_AUTODOC_EVENTS]:
                Function return annotation as a string of the form " -> annotation",
                or None if there is no return annotation.
        :return:
            [SPHINX_AUTODOC_EVENTS]:
                The event handler can return a new tuple (signature, return_annotation)
                to change what Sphinx puts into the output.
        """
        sphinxdebug("PyDoc.autodocprocesssignature(what=%r, fq_name=%r, obj=%r, options=%r, signature=%r, return_annotation=%r)",
                    what, fq_name, obj, options, signature, return_annotation)

        # Useful local functions.
        def _debug(fmt, *args):  # type: (str, typing.Any) -> None
            sphinxdebug("PyDoc.autodoc-process-signature(): " + fmt, *args)

        def _errmsg(message):  # type: (str) -> str
            return f"autodoc-process-signature(fq_name={fq_name!r}): {message}"

        if what == "class":
            # Do not show `__init__()` arguments in the class signature.
            # `__init__()` documentation is generated separately.
            _debug("Class %s signature set from %r to None", fq_name, signature)
            return None, None

        if signature and ("#" in signature):
            # As of sphinx@4.4.0, additional trailing comments after `# type: ...` comments are not automatically removed.
            # Let's remove them below.
            _debug("Removing comments from signature %r", signature)

            # Split the comma-separated argument list.
            assert signature.startswith("(") and signature.endswith(")")
            _args = signature[1:-1].split(", ")  # type: typing.List[str]

            # Restore commas which were not to seperate arguments.
            _index = 0  # type: int
            while _index < len(_args):
                # Check whether the argument line actually starts with a typed argument name.
                if re.search(r"^\w+: ", _args[_index]):
                    _debug("  => arg#%d %r", _index + 1, _args[_index])
                    _index += 1
                else:
                    assert _index > 0, _errmsg(f"Unexpected {_args[_index]!r} at the beginning of signature {signature!r}")
                    _debug("     Merging %r + %r", _args[_index - 1], _args[_index])
                    _args[_index - 1] += f", {_args[_index]}"  # Don't forget to restore the comma.
                    del _args[_index]

            # Remove comments.
            for _index in range(len(_args)):  # Type already declared above.
                if "#" in _args[_index]:
                    _debug("  => Removing comment from arg#%d %r", _index + 1, _args[_index])
                    _match = (
                        # First try to match with a default value pattern at the end of the line.
                        re.match(r"^([^#]+)( *#.*)( = \w+)$", _args[_index])
                        # Otherwise match with no default value.
                        # The empty group in the end is left intentionally for grouping compatibility between the two regex.
                        or re.match(r"^([^#]+)( *#.*)()$", _args[_index])
                    )  # type: typing.Optional[typing.Match[str]]
                    assert _match, _errmsg(f"Could not parse comment from {_args[_index]!r}")
                    _args[_index] = _match.group(1).rstrip() + _match.group(3)
                    _debug("     %r", _args[_index])

            # Rebuild and return the signature.
            signature = f"({', '.join(_args)})"
            _debug("Final signature: %r", signature)
            return signature, return_annotation

        return None

    def autodoc_objectdescription(
            self,
            object,  # type: typing.Any  # noqa  ## Shadows built-in name 'object'
    ):  # type: (...) -> str
        """
        Replacement hack for ``sphinx.ext.autodoc.object_description()``.

        :param object: Caution! may be ``None``.
        :raise ValueError:
            When ``object`` is ``None``,
            so that *autodoc* does not print out erroneous attribute values,
            especially for instance attribute.

        .. note::
            The signature follows strictly the one of ``sphinx.util.inspect.object_description()``
            in order to avoid typing errors when setting this method as a replacement for ``sphinx.ext.autodoc.object_description()``.

        .. warning::
            Unfortunately, it seems we have no way to differenciate class and instance attributes when the value is ``None``
            (see `sphinx#904 <https://github.com/sphinx-doc/sphinx/issues/904>`_).
        """
        if object is None:
            raise ValueError("No value for data/attributes")
        from sphinx.util.inspect import object_description
        return object_description(object)

    def autodoc_processdocstring(
            self,
            app,  # type: sphinx.application.Sphinx
            what,  # type: str
            fq_name,  # type: str
            obj,  # type: typing.Optional[typing.Any]
            options,  # type: typing.Any
            lines,  # type: typing.List[str]
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-process-docstring

        [SPHINX_AUTODOC_EVENTS]:
            autodoc-process-docstring(app, what, name, obj, options, lines)

            Emitted when autodoc has read and processed a docstring. lines is a list of strings – the lines of the processed docstring –
            that the event handler can modify in place to change what Sphinx puts into the output.

        :param app:
            [SPHINX_AUTODOC_EVENTS]:
                The Sphinx application object
        :param what:
            [SPHINX_AUTODOC_EVENTS]:
                The type of the object which the docstring belongs to
                (one of "module", "class", "exception", "function", "method", "attribute")

            .. note:: Actually is the type of the current object, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param fq_name:
            ``name`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                The fully qualified name of the object

            .. note:: Actually is the fully qualified name, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param obj:
            [SPHINX_AUTODOC_EVENTS]:
                The object itself

            .. warning:: May be None, especially for attributes.
        :param options:
            [SPHINX_AUTODOC_EVENTS]:
                The options given to the directive:
                an object with attributes inherited_members, undoc_members, show_inheritance and noindex
                that are true if the flag option of same name was given to the auto directive"
        :param lines:
            [SPHINX_AUTODOC_EVENTS]:
                The lines of the docstring, see above

        Ensures Python items are documented.
        If not, prints a warning in the console and generates a warning in the output documentation.
        """
        sphinxdebug("PyDoc.autodocprocessdocstring(what=%r, fq_name=%r, obj=%r, options=%r, lines=%r)",
                    what, fq_name, obj, options, lines)

        # Check whether the item is documented.
        # Inspired from: https://stackoverflow.com/questions/14141170/how-can-i-just-list-undocumented-members-with-sphinx-autodoc
        # By default, check the docstring in `lines` (which may come from the upper classes) is not empty.
        _is_documented = (len(lines) > 0)  # type: bool
        if (obj is not None) and self._isspecialfunction(obj):
            # Do not check the `lines` parameters for special functions,
            # in as much as sphinx-build automatically fills this parameter with what is inherited from the base builtin types (usually `object`).
            _is_documented = (obj.__doc__ is not None)
        elif (obj is not None) and isinstance(obj, enum.EnumMeta):
            # Do not check the `lines` parameters for enums,
            # in as much as `sphinx-build` automatically fills this parameter with the defaut :class:`enum.Enum`'s docstring.
            _is_documented = (lines != ["An enumeration.", ""])
        if not _is_documented:
            # If not:
            # - Display a warning in the console during the build.
            sphinxwarning(f"Undocumented {what} `{fq_name}`")
            # - Display a warning in the output documentation.
            if PyDoc.WARN_IN_DOC:
                lines.append(f".. warning:: Undocumented {what} ``{fq_name}``.")

        # Identify the items to track when applicable.
        if inspect.ismodule(obj):
            self._trackmoduleitems(obj)

        # Remove this item from the tracked item list.
        if fq_name in self._tracked_items:
            sphinxdebug("Tracked %s `%s` found", what, fq_name)
            _item_type = self._tracked_items.pop(fq_name)  # type: str
            if _item_type != what:
                sphinxwarning(f"Unexpected type {what} for {_item_type} `{fq_name}`")

        # Memorize the documented item.
        self._documented_items[fq_name] = PyDoc.DocumentedItem(what, obj, lines)

    def _fqname(
            self,
            obj,  # type: typing.Any
    ):  # type: (...) -> str
        if inspect.ismodule(obj):
            return str(obj.__name__)
        return f"{inspect.getmodule(obj)}.{obj.__name__}"

    def _trackmoduleitems(
            self,
            module,  # type: types.ModuleType
    ):  # type: (...) -> None
        """
        Identify items to track from a Python module, especially attributes.

        :param module: Module to track items from.

        .. warning:: Does not track untyped attributes.
        """
        import sphinx.pycode

        sphinxdebug("PyDoc._trackmoduleitems(module=%r)", module)

        assert inspect.ismodule(module), f"Not a module {module!r}"
        _parser = sphinx.pycode.Parser(inspect.getsource(module))  # type: sphinx.pycode.Parser
        _parser.parse()
        for _class_name, _attr_name in _parser.annotations:  # type: str, str
            _track_item = True  # type: bool

            # Do not track private attributes.
            if _attr_name.startswith("__"):
                continue
            if _class_name:
                _fq_name = f"{module.__name__}.{_class_name}.{_attr_name}"  # type: str
                _item_type = "attribute"  # type: str
            else:
                _fq_name = f"{module.__name__}.{_attr_name}"
                _item_type = "data"
                if module.__doc__:
                    for _line in module.__doc__.splitlines():  # type: str
                        if re.match(r"\.\. py:attribute:: %s" % _attr_name, _line):
                            sphinxdebug("Attribute '%s' already described in the '%s' module docstring. No need to track it.", _attr_name, module.__name__)
                            _track_item = False
                            break
                if _track_item:
                    sphinxwarning(f"Missing `.. py:attribute::` directive for attribute '{_attr_name}' in module '{module.__name__}'")

            if _track_item:
                sphinxdebug("Tracking %s `%s`", _item_type, _fq_name)
                self._tracked_items[_fq_name] = _item_type

    def _isspecialfunction(
            self,
            obj,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Due to [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808), it seems preferrable to rely on the actual object,
        rather than the ``what`` and ``name`` parameters, in this class's *autodoc* handlers,
        which behaviour does not always conform to their respective documentation.

        Inspired from:
        - https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method
        - https://docs.python.org/3/reference/datamodel.html
        """
        return (inspect.isfunction(obj) or inspect.ismethod(obj)) and (obj.__name__ in (
            # 3. Data model (https://docs.python.org/3/reference/datamodel.html#data-model)
            # 3.1. Objects, values and types (https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)
            # 3.2. The standard type hierarchy (https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy)
            #     Memo: Interesting description about special attributes.
            # 3.3. Special method names (https://docs.python.org/3/reference/datamodel.html#special-method-names)
            # 3.3.1. Basic customization (https://docs.python.org/3/reference/datamodel.html#basic-customization).
            "__new__",              # https://docs.python.org/3/reference/datamodel.html#object.__new__
            "__init__",             # https://docs.python.org/3/reference/datamodel.html#object.__init__
            "__del__",              # https://docs.python.org/3/reference/datamodel.html#object.__del__
            "__repr__",             # https://docs.python.org/3/reference/datamodel.html#object.__repr__
            "__str__",              # https://docs.python.org/3/reference/datamodel.html#object.__str__
            "__bytes__",            # https://docs.python.org/3/reference/datamodel.html#object.__bytes__
            "__format__",           # https://docs.python.org/3/reference/datamodel.html#object.__format__
            "__lt__",               # https://docs.python.org/3/reference/datamodel.html#object.__lt__
            "__le__",               # https://docs.python.org/3/reference/datamodel.html#object.__le__
            "__eq__",               # https://docs.python.org/3/reference/datamodel.html#object.__eq__
            "__ne__",               # https://docs.python.org/3/reference/datamodel.html#object.__ne__
            "__gt__",               # https://docs.python.org/3/reference/datamodel.html#object.__gt__
            "__ge__",               # https://docs.python.org/3/reference/datamodel.html#object.__ge__
            "__hash__",             # https://docs.python.org/3/reference/datamodel.html#object.__hash__
            "__bool__",             # https://docs.python.org/3/reference/datamodel.html#object.__bool__
            # 3.3.2. Customizing attribute access (https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access)
            "__getattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__getattr__
            "__getattributes__",    # https://docs.python.org/3/reference/datamodel.html#object.__getattribute__
            "__setattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__setattr__
            "__delattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__delattr__
            "__dir__",              # https://docs.python.org/3/reference/datamodel.html#object.__dir__
            # 3.3.2.1. Customizing module attribute access (https://docs.python.org/3/reference/datamodel.html#customizing-module-attribute-access)
            # 3.3.2.2. Implementing Descriptors (https://docs.python.org/3/reference/datamodel.html#implementing-descriptors)
            "__get__",              # https://docs.python.org/3/reference/datamodel.html#object.__get__
            "__set__",              # https://docs.python.org/3/reference/datamodel.html#object.__set__
            "__delete__",           # https://docs.python.org/3/reference/datamodel.html#object.__delete__
            # 3.3.2.3. Invoking Descriptors (https://docs.python.org/3/reference/datamodel.html#invoking-descriptors)
            # 3.3.2.4. __slots__ (https://docs.python.org/3/reference/datamodel.html#slots)
            "__slots__",            # https://docs.python.org/3/reference/datamodel.html#object.__slots__
            # 3.3.2.4.1. Notes on using __slots__ (https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots)
            # 3.3.3. Customizing class creation (https://docs.python.org/3/reference/datamodel.html#customizing-class-creation)
            "__init_subclass__",    # https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
            "__set_name__",         # https://docs.python.org/3/reference/datamodel.html#object.__set_name__
            # 3.3.3.1. Metaclasses (https://docs.python.org/3/reference/datamodel.html#metaclasses)
            # 3.3.3.2. Resolving MRO entries (https://docs.python.org/3/reference/datamodel.html#resolving-mro-entries)
            # 3.3.3.3. Determining the appropriate metaclass (https://docs.python.org/3/reference/datamodel.html#determining-the-appropriate-metaclass)
            # 3.3.3.4. Preparing the class namespace (https://docs.python.org/3/reference/datamodel.html#preparing-the-class-namespace)
            # 3.3.3.5. Executing the class body (https://docs.python.org/3/reference/datamodel.html#executing-the-class-body)
            # 3.3.3.6. Creating the class object (https://docs.python.org/3/reference/datamodel.html#creating-the-class-object)
            # 3.3.3.7. Uses for metaclasses (https://docs.python.org/3/reference/datamodel.html#uses-for-metaclasses)
            # 3.3.4. Customizing instance and subclass checks (https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks)
            "__instancecheck__",    # https://docs.python.org/3/reference/datamodel.html#class.__instancecheck__
            "__subclasscheck__",    # https://docs.python.org/3/reference/datamodel.html#class.__subclasscheck__
            # 3.3.5. Emulating generic types (https://docs.python.org/3/reference/datamodel.html#emulating-generic-types)
            "__class_getitem__",    # https://docs.python.org/3/reference/datamodel.html#object.__class_getitem__
            # 3.3.5.1. The purpose of __class_getitem__ (https://docs.python.org/3/reference/datamodel.html#the-purpose-of-class-getitem)
            # 3.3.5.2. __class_getitem__ versus __getitem__ (https://docs.python.org/3/reference/datamodel.html#class-getitem-versus-getitem)
            # 3.3.6. Emulating callable objects (https://docs.python.org/3/reference/datamodel.html#emulating-callable-objects)
            "__call__",             # https://docs.python.org/3/reference/datamodel.html#object.__call__
            # 3.3.7. Emulating container types (https://docs.python.org/3/reference/datamodel.html#emulating-container-types)
            "__len__",              # https://docs.python.org/3/reference/datamodel.html#object.__len__
            "__length_hint__",      # https://docs.python.org/3/reference/datamodel.html#object.__length_hint__
            "__getitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__getitem__
            "__setitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__setitem__
            "__delitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__delitem__
            "__missing__",          # https://docs.python.org/3/reference/datamodel.html#object.__missing__
            "__iter__",             # https://docs.python.org/3/reference/datamodel.html#object.__iter__
            "__reversed__",         # https://docs.python.org/3/reference/datamodel.html#object.__reversed__
            "__contains__",         # https://docs.python.org/3/reference/datamodel.html#object.__contains__
            # 3.3.8. Emulating numeric types (https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types)
            "__add__",              # https://docs.python.org/3/reference/datamodel.html#object.__add__
            "__sub__",              # https://docs.python.org/3/reference/datamodel.html#object.__sub__
            "__mul__",              # https://docs.python.org/3/reference/datamodel.html#object.__mul__
            "__matmul__",           # https://docs.python.org/3/reference/datamodel.html#object.__matmul__
            "__truediv__",          # https://docs.python.org/3/reference/datamodel.html#object.__truediv__
            "__floordiv__",         # https://docs.python.org/3/reference/datamodel.html#object.__floordiv__
            "__mod__",              # https://docs.python.org/3/reference/datamodel.html#object.__mod__
            "__divmod__",           # https://docs.python.org/3/reference/datamodel.html#object.__divmod__
            "__pow__",              # https://docs.python.org/3/reference/datamodel.html#object.__pow__
            "__lshift__",           # https://docs.python.org/3/reference/datamodel.html#object.__lshift__
            "__rshift__",           # https://docs.python.org/3/reference/datamodel.html#object.__rshift__
            "__and__",              # https://docs.python.org/3/reference/datamodel.html#object.__and__
            "__xor__",              # https://docs.python.org/3/reference/datamodel.html#object.__xor__
            "__or__",               # https://docs.python.org/3/reference/datamodel.html#object.__or__
            "__radd__",             # https://docs.python.org/3/reference/datamodel.html#object.__radd__
            "__rsub__",             # https://docs.python.org/3/reference/datamodel.html#object.__rsub__
            "__rmul__",             # https://docs.python.org/3/reference/datamodel.html#object.__rmul__
            "__rmatmul__",          # https://docs.python.org/3/reference/datamodel.html#object.__rmatmul__
            "__rtruediv__",         # https://docs.python.org/3/reference/datamodel.html#object.__rtruediv__
            "__rfloordiv__",        # https://docs.python.org/3/reference/datamodel.html#object.__rfloordiv__
            "__rmod__",             # https://docs.python.org/3/reference/datamodel.html#object.__rmod__
            "__rdivmod__",          # https://docs.python.org/3/reference/datamodel.html#object.__rdivmod__
            "__rpow__",             # https://docs.python.org/3/reference/datamodel.html#object.__rpow__
            "__rlshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__rlshift__
            "__rrshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__rrshift__
            "__rand__",             # https://docs.python.org/3/reference/datamodel.html#object.__rand__
            "__rxor__",             # https://docs.python.org/3/reference/datamodel.html#object.__rxor__
            "__ror__",              # https://docs.python.org/3/reference/datamodel.html#object.__ror__
            "__iadd__",             # https://docs.python.org/3/reference/datamodel.html#object.__iadd__
            "__isub__",             # https://docs.python.org/3/reference/datamodel.html#object.__isub__
            "__imul__",             # https://docs.python.org/3/reference/datamodel.html#object.__imul__
            "__imatmul__",          # https://docs.python.org/3/reference/datamodel.html#object.__imatmul__
            "__itruediv__",         # https://docs.python.org/3/reference/datamodel.html#object.__itruediv__
            "__ifloordiv__",        # https://docs.python.org/3/reference/datamodel.html#object.__ifloordiv__
            "__imod__",             # https://docs.python.org/3/reference/datamodel.html#object.__imod__
            "__ipow__",             # https://docs.python.org/3/reference/datamodel.html#object.__ipow__
            "__ilshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__ilshift__
            "__irshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__irshift__
            "__iand__",             # https://docs.python.org/3/reference/datamodel.html#object.__iand__
            "__ixor__",             # https://docs.python.org/3/reference/datamodel.html#object.__ixor__
            "__ior__",              # https://docs.python.org/3/reference/datamodel.html#object.__ior__
            "__neg__",              # https://docs.python.org/3/reference/datamodel.html#object.__neg__
            "__pos__",              # https://docs.python.org/3/reference/datamodel.html#object.__pos__
            "__abs__",              # https://docs.python.org/3/reference/datamodel.html#object.__abs__
            "__invert__",           # https://docs.python.org/3/reference/datamodel.html#object.__invert__
            "__complex__",          # https://docs.python.org/3/reference/datamodel.html#object.__complex__
            "__int__",              # https://docs.python.org/3/reference/datamodel.html#object.__int__
            "__float__",            # https://docs.python.org/3/reference/datamodel.html#object.__float__
            "__index__",            # https://docs.python.org/3/reference/datamodel.html#object.__index__
            "__round__",            # https://docs.python.org/3/reference/datamodel.html#object.__round__
            "__trunc__",            # https://docs.python.org/3/reference/datamodel.html#object.__trunc__
            "__floor__",            # https://docs.python.org/3/reference/datamodel.html#object.__floor__
            "__ceil__",             # https://docs.python.org/3/reference/datamodel.html#object.__ceil__
            # 3.3.9. With Statement Context Managers (https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers)
            "__enter__",            # https://docs.python.org/3/reference/datamodel.html#object.__enter__
            "__exit__",             # https://docs.python.org/3/reference/datamodel.html#object.__exit__
            # 3.3.10. Customizing positional arguments in class pattern matching
            #         (https://docs.python.org/3/reference/datamodel.html#customizing-positional-arguments-in-class-pattern-matching)
            # 3.3.11. Special method lookup (https://docs.python.org/3/reference/datamodel.html#special-method-lookup)
            # 3.4. Coroutines (https://docs.python.org/3/reference/datamodel.html#coroutines)
            # 3.4.1. Awaitable Objects (https://docs.python.org/3/reference/datamodel.html#awaitable-objects)
            "__await__",            # https://docs.python.org/3/reference/datamodel.html#object.__await__
            # 3.4.2. Coroutine Objects (https://docs.python.org/3/reference/datamodel.html#coroutine-objects)
            # 3.4.3. Asynchronous Iterators (https://docs.python.org/3/reference/datamodel.html#asynchronous-iterators)
            "__aiter__",            # https://docs.python.org/3/reference/datamodel.html#object.__aiter__
            "__anext__",            # https://docs.python.org/3/reference/datamodel.html#object.__anext__
            # 3.4.4. Asynchronous Context Managers (https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
            "__aenter__",           # https://docs.python.org/3/reference/datamodel.html#object.__aenter__
            "__aexit__",            # https://docs.python.org/3/reference/datamodel.html#object.__aexit__

            # Other special methods.
            "__fspath__",           # https://docs.python.org/3/library/os.html#os.PathLike.__fspath__
        ))

    def _warnundocitems(self):  # type: (...) -> None
        # Print out console warnings for non documented tracked items.
        for _undoc_fq_name in self._tracked_items:  # type: str
            sphinxwarning(f"Undocumented {self._tracked_items[_undoc_fq_name]} `{_undoc_fq_name}`")
            if PyDoc.WARN_IN_DOC:
                sphinxwarning(f"Undocumented {self._tracked_items[_undoc_fq_name]} `{_undoc_fq_name}` "
                              "could not be mentioned directly in the output documentation.")

        # Reset the documented and tracked item lists.
        self._documented_items.clear()
        self._tracked_items.clear()

    def _simplifyreferences(
            self,
            docname,  # type: str
            element,  # type: docutils.nodes.Element
            debug_indentation="",  # type: str
            short_ref=None,  # type: str
    ):  # type: (...) -> None
        sphinxdebug("%sPyDoc._simplifyreferences(docname=%r, element=%r, short_ref=%r): element.attributes=%r",
                    debug_indentation, docname, element, short_ref, element.attributes)

        # :class:`docutils.nodes.reference` node: determine the short reference when applicable.
        if isinstance(element, docutils.nodes.reference):
            _reference = element  # type: docutils.nodes.reference
            _reftitle = _reference.get("reftitle", "")  # type: str
            _match = re.match(r"^scenario\.([a-z0-9]+)\.(.*)", _reftitle)
            if _match:
                short_ref = _match.group(2)
            else:
                sphinxdebug("%sPyDoc._simplifyreferences(docname=%r): 'reftitle' %r does not match pattern",
                            debug_indentation, docname, _reftitle)

        for _child_index in range(len(element.children)):  # type: int
            _child = element.children[_child_index]  # type: docutils.nodes.Node
            if isinstance(_child, docutils.nodes.Text):
                # Text children: simplify the text when `short_ref` is set.
                if short_ref is not None:
                    _short_ref = short_ref  # type: str
                    if _child.endswith("()"):
                        _short_ref += "()"
                    if _short_ref.endswith(_child):
                        sphinxdebug("%sPyDoc._simplifyreferences(docname=%r): Text %r is even shorter than %r, don't change it",
                                    debug_indentation, docname, _child, short_ref)
                    elif _child.endswith(_short_ref):
                        sphinxdebug("%sPyDoc._simplifyreferences(docname=%r): Simplifying %r >> %r",
                                    debug_indentation, docname, _child, _short_ref)
                        element.children[_child_index] = docutils.nodes.Text(_short_ref)
                    else:
                        sphinxwarning(f"{docname}: Mismatching text {_child!r} with expected short reference {short_ref!r}")
            elif isinstance(_child, docutils.nodes.Element):
                # Element children: make recursive calls.
                self._simplifyreferences(docname, _child, debug_indentation=f"{debug_indentation} ", short_ref=short_ref)
            else:
                sphinxwarning(f"{docname}: Unexpected kind of node {_child!r}")
