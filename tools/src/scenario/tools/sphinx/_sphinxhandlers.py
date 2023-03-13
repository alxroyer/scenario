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

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        # See [SPHINX_CORE_EVENTS] https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
        # for an overview of events that happen during a build.
        #
        # 1. event.config-inited(app,config)
        app.connect("config-inited", self.configinited)

        # 2. event.builder-inited(app)
        app.connect("builder-inited", self.builderinited)

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
        from ._sphinxlogging import SphinxLogger
        from .._paths import DOC_SRC_PATH
        from ..mkdoc import MkDoc

        _logger = SphinxLogger("sphinx:config-inited", enable_debug=True)  # type: SphinxLogger

        _logger.debug("configinited()")

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
        MkDoc().sphinxapidoc()

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
        from ._sphinxlogging import SphinxLogger

        _logger = SphinxLogger("sphinx:builder-inited", enable_debug=True)  # type: SphinxLogger

        _logger.debug("SphinxHendlers.builderinited()")

    def envupdated(
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
        from ._documenteditems import warnundocitems
        from ._sphinxlogging import SphinxLogger

        _logger = SphinxLogger("sphinx:env-updated", enable_debug=True)  # type: SphinxLogger

        _logger.debug("envupdated(env=%r)", env)

        warnundocitems()

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
        from ._references import simplifyreferences
        from ._sphinxlogging import SphinxLogger

        _logger = SphinxLogger("sphinx:doctreee-resolved", enable_debug=True)  # type: SphinxLogger

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
        from ._sphinxlogging import SphinxLogger

        _logger = SphinxLogger("sphinx:build-finished", enable_debug=True)  # type: SphinxLogger

        _logger.debug("SohinxHandlers.buildfinished(exception=%r)", exception)