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

"""
Defines a :class:`Logger` class that makes it possible to:

- log messages with both the Sphinx and `scenario` loggers:

  - Debug messages are displayed using the `scenario` logging system,
    in order to benefit from our useful logging capabilities (debug enabling, log classes, indentation...)
  - Higher log levels are displayed as user messages with the regular Sphinx logger,
    and duplicated as debug messages through the `scenario` logging system (makes it possible to `grep` in the output log, using the log class).

- tune precisely which :mod:`scenario.tools.sphinx` debug logging to activate:

  - The 'tools/conf/sphinx/debug.yml' configuration file defines which log classes should be enabled for debug.
"""

import logging
import typing

import scenario


def loggingsetup():  # type: (...) -> None
    from .._paths import TOOLS_CONF_PATH

    # Load 'tools/conf/sphinx/debug.yml' debug configurations.
    scenario.Args.setinstance(scenario.Args(class_debugging=True))
    scenario.Args.getinstance().parse(["--config-file", str(TOOLS_CONF_PATH / "sphinx" / "debug.yml")])


def savesphinxverbosity(
        verbosity,  # type: int
):  # type: (...) -> None
    scenario.Args.getinstance().debug_main = (verbosity > 0)


def sphinxlogger():  # type: (...) -> logging.Logger
    return logging.getLogger("sphinx")


class Logger:

    class Id(scenario.enum.StrEnum):
        # Sphinx handlers.
        SPHINX_CONFIG_INITED = "sphinx:config-inited"
        SPHINX_BUILDER_INITED = "sphinx:builder-inited"
        SPHINX_ENV_BEFORE_READ_DOCS = "sphinx:env-before-read-docs"
        SPHINX_SOURCE_READ = "sphinx:source-read"
        SPHINX_DOCTREE_READ = "sphinx:doctree-read"
        SPHINX_ENV_UPDATED = "sphinx:env-updated"
        SPHINX_MISSING_REFERENCE = "sphinx:missing-reference"
        SPHINX_DOCTREE_RESOLVED = "sphinx:doctreee-resolved"
        SPHINX_BUILD_FINISHED = "sphinx:build-finished"
        # Autodoc handlers.
        AUTODOC_SKIP_MEMBER = "autodoc:skip-member"
        AUTODOC_PROCESS_SIGNATURE = "autodoc:process-signature"
        AUTODOC_PROCESS_DOCSTRING = "autodoc:process-docstring"
        # Sphinx hacking.
        PARSE_REFTARGET_HACK = "parse-reftarget-hack"
        OBJECT_DESCRIPTION_HACK = "object-description-hack"

        # Type hints.
        TYPE_CHECKING_RELOAD = "type-checking-reload"
        TRACK_SCENARIO_TYPES = "track-scenario-types"
        CONFIGURE_TYPE_ALIASES = "configure-type-aliases"
        # Documented items.
        TRACK_DOCUMENTED_ITEMS = "track-documented-items"
        # References.
        SIMPLIFY_REFERENCES = "simplify-references"

    _db = {}  # type: typing.Dict[Logger.Id, Logger]

    @staticmethod
    def getinstance(
            id,  # type: Logger.Id  # noqa  ## Shadows built-in name 'id'
    ):  # type: (...) -> Logger
        if id not in Logger._db:
            Logger._db[id] = Logger(id)
        return Logger._db[id]

    def __init__(
            self,
            id,  # type: Logger.Id  # noqa  ## Shadows built-in name 'id'
    ):  # type: (...) -> None
        self.scenario_logger = scenario.Logger(f"scenario.tools.sphinx:{id}")  # type: scenario.Logger

        # Don't make scenario debug logging depend on Sphinx verbosity.
        # Sphinx debugging info (with the `-vv` option) is really verbose.
        # It's worth enabling `scenario.tools.sphinx` debugging without pulling Sphinx verbosity.

        # if not scenario.Args.getinstance().debug_main:
        #     self.scenario_logger.enabledebug(False)

    def debug(
            self,
            fmt,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        self.scenario_logger.debug(fmt, *args)

    def info(
            self,
            fmt,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        self.debug(f"INFO: {fmt}", *args)
        sphinxlogger().info(fmt, *args)

    def warning(
            self,
            fmt,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        self.debug(f"WARNING: {fmt}", *args)
        sphinxlogger().warning(f"WARNING: {fmt}", *args)

    def error(
            self,
            fmt,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        self.debug(f"ERROR: {fmt}", *args)
        sphinxlogger().error(f"ERROR: {fmt}", *args)
