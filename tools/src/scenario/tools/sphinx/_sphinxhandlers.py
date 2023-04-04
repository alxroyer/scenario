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

import docutils.nodes
import pathlib
import sphinx.application
import typing


class SphinxHandlers:
    """
    See [SPHINX_CORE_EVENTS] https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
    for an overview of events that happen during a build.
    """

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        # 1. event.config-inited(app,config)
        app.connect("config-inited", self.configinited)

        # 2. event.builder-inited(app)
        app.connect("builder-inited", self.builderinited)

        # 3. event.env-get-outdated(app, env, added, changed, removed)
        # 4. event.env-before-read-docs(app, env, docnames)
        app.connect("env-before-read-docs", self.envbeforereaddocs)

        # for docname in docnames:
        #    5. event.env-purge-doc(app, env, docname)
        #
        #    if doc changed and not removed:
        #       6. source-read(app, docname, source)
        app.connect("source-read", self.sourceread)
        #       7. run source parsers: text -> docutils.document
        #          - parsers can be added with the app.add_source_parser() API
        #       8. apply transforms based on priority: docutils.document -> docutils.document
        #          - event.doctree-read(app, doctree) is called in the middle of transforms,
        #            transforms come before/after this event depending on their priority.
        app.connect("doctree-read", self.doctreeread)

        # 9. event.env-merge-info(app, env, docnames, other)
        #    - if running in parallel mode, this event will be emitted for each process

        # 10. event.env-updated(app, env)
        app.connect("env-updated", self.envupdated)
        # 11. event.env-get-updated(app, env)
        # 12. event.env-check-consistency(app, env)

        # The updated-docs list can be builder dependent, but generally includes all new/changed documents,
        # plus any output from `env-get-updated`, and then all "parent" documents in the ToC tree
        # For builders that output a single page, they are first joined into a single doctree before post-transforms
        # or the doctree-resolved event is emitted

        # for docname in updated-docs:
        #    13. apply post-transforms (by priority): docutils.document -> docutils.document
        #    14. event.doctree-resolved(app, doctree, docname)
        #        - In the event that any reference nodes fail to resolve, the following may emit:
        #        - event.missing-reference(env, node, contnode)
        #        - event.warn-missing-reference(domain, node)
        app.connect("doctree-resolved", self.doctreeresolved)
        app.connect("missing-reference", self.missingreference)

        # 15. Generate output files
        # 16. event.build-finished(app, exception)
        app.connect("build-finished", self.buildfinished)

    def configinited(
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
        from .._paths import DOC_SRC_PATH
        from ._commands import sphinxapidoc
        from ._logging import Logger, savesphinxverbosity

        savesphinxverbosity(app.verbosity)

        _logger = Logger.getinstance(Logger.Id.SPHINX_CONFIG_INITED)  # type: Logger
        _logger.debug("configinited()")

        _logger.debug("app.verbosity=%r", app.verbosity)
        _logger.debug("app.confdir=%r", app.confdir)
        _logger.debug("app.doctreedir=%r", app.doctreedir)
        _logger.debug("app.outdir=%r", app.outdir)
        _logger.debug("app.srcdir=%r", app.srcdir)

        # Fix 'doc/src/' path if needed.
        # Particularly useful when buiding on 'readthedocs.io'.
        if pathlib.Path(app.srcdir) != DOC_SRC_PATH:
            _logger.info(f"Fixing source directory from {app.srcdir!r} to {DOC_SRC_PATH.abspath!r}")
            app.srcdir = DOC_SRC_PATH.abspath

        # Update 'doc/src/py/' files.
        sphinxapidoc()

    def builderinited(
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
        from ._logging import Logger

        _logger = Logger.getinstance(Logger.Id.SPHINX_BUILDER_INITED)  # type: Logger
        _logger.debug("SphinxHendlers.builderinited()")

    def envbeforereaddocs(
            self,
            app,  # type: sphinx.application.Sphinx
            env,  # type: sphinx.application.BuildEnvironment
            docnames,  # type: typing.Sequence[str]
    ):  # type: (...) -> typing.Any
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-env-before-read-docs

        [SPHINX_CORE_EVENTS]:
            Emitted after the environment has determined the list of all added and changed files and just before it reads them.
            It allows extension authors to reorder the list of docnames (inplace) before processing,
            or add more docnames that Sphinx did not consider changed
            (but never add any docnames that are not in env.found_docs).

            You can also remove document names; do this with caution since it will make Sphinx treat changed files as unchanged.
        """
        from ._logging import Logger
        from ._reflection import reloadscenariowithtypechecking

        _logger = Logger(Logger.Id.SPHINX_ENV_BEFORE_READ_DOCS)  # type: Logger
        _logger.debug("envbeforereaddocs(env=%r, docnames=%r)", env, docnames)

        _logger.debug("Reloading `scenario` modules with `typing.TYPE_CHECKING` enabled")
        reloadscenariowithtypechecking()

    def sourceread(
            self,
            app,  # type: sphinx.application.Sphinx
            docname,  # type: str
            source,  # type: typing.List[str]
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-source-read

        [SPHINX_CORE_EVENTS]:
            source-read(app, docname, source)

            Emitted when a source file has been read.
            The source argument is a list whose single element is the contents of the source file.
            You can process the contents and replace this item to implement source-level transformations.

            For example, if you want to use $ signs to delimit inline math, like in LaTeX,
            you can use a regular expression to replace ``$...$`` by ``:math:`...```.
        """
        from ._logging import Logger

        _logger = Logger(Logger.Id.SPHINX_SOURCE_READ)  # type: Logger
        _logger.debug("sourceread(docname=%r, source=%r)", docname, source)

    def doctreeread(
            self,
            app,  # type: sphinx.application.Sphinx
            doctree,  # type: docutils.nodes.document
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-doctree-read

        [SPHINX_CORE_EVENTS]:
            doctree-read(app, doctree)

            Emitted when a doctree has been parsed and read by the environment, and is about to be pickled.
            The doctree can be modified in-place.
        """
        from ._logging import Logger

        _logger = Logger(Logger.Id.SPHINX_DOCTREE_READ)  # type: Logger
        _logger.debug("doctreeread(doctree=%r)", doctree)

    def envupdated(
            self,
            app,  # type: sphinx.application.Sphinx
            env,  # type: sphinx.application.BuildEnvironment
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-env-updated

        [SPHINX_CORE_EVENTS]:
            env-updated(app, env)

            Emitted when the update() method of the build environment has completed, that is, the environment and all doctrees are now up-to-date.

            You can return an iterable of docnames from the handler. These documents will then be considered updated,
            and will be (re-)written during the writing phase.
        """
        from ._documenteditems import warnundocitems
        from ._logging import Logger

        _logger = Logger(Logger.Id.SPHINX_ENV_UPDATED)  # type: Logger
        _logger.debug("envupdated(env=%r)", env)

        warnundocitems()

    def missingreference(
            self,
            app,  # type: sphinx.application.Sphinx
            env,  # type: sphinx.application.BuildEnvironment
            node,  # type: docutils.nodes.Node
            contnode,  # type: docutils.nodes.Node
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-missing-reference

        [SPHINX_CORE_EVENTS]:
            Emitted when a cross-reference to an object cannot be resolved.
            If the event handler can resolve the reference,
            it should return a new docutils node to be inserted in the document tree in place of the node ``node``.
            Usually this node is a ``reference`` node containing ``contnode`` as a child.
            If the handler can not resolve the cross-reference, it can either return None to let other handlers try,
            or raise ``NoUri`` to prevent other handlers in trying and suppress a warning about this cross-reference being unresolved.

        :param app:
        :param env:
            [SPHINX_CORE_EVENTS]:
                The build environment (``app.builder.env``).
        :param node:
            [SPHINX_CORE_EVENTS]:
                The ``pending_xref`` node to be resolved.
                Its attributes ``reftype``, ``reftarget``, ``modname`` and ``classname`` attributes determine the type and target of the reference.
        :param contnode:
            [SPHINX_CORE_EVENTS]:
                The node that carries the text and formatting inside the future reference and should be a child of the returned reference node.
        """
        from ._logging import Logger

        _logger = Logger.getinstance(Logger.Id.SPHINX_MISSING_REFERENCE)  # type: Logger
        _logger.debug("missingreference(env=%r, node=%r, contnode=%r)", env, node, contnode)

        if node.source and node.line:
            if contnode.astext() in (
                "DemoArgs",
                "scenario.test",
                "scenario.tools",
                "scenario.tools.data.scenarios",
            ):
                return

            _logger.warning(f"{node.source}:{node.line}: Reference missing {contnode.astext()}")

    def doctreeresolved(
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
        from ._logging import Logger
        from ._references import simplifyreferences

        _logger = Logger.getinstance(Logger.Id.SPHINX_DOCTREE_RESOLVED)  # type: Logger
        _logger.debug("SphincHandlers.doctreeresolved(doctree=%r, docname=%r)", doctree, docname)

        simplifyreferences(docname, doctree)

    def buildfinished(
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
        from ._logging import Logger

        _logger = Logger.getinstance(Logger.Id.SPHINX_BUILD_FINISHED)  # type: Logger
        _logger.debug("SphinxHandlers.buildfinished(exception=%r)", exception)
