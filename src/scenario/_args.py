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
Base module for program arguments management.

:meth:`Args.getinstance()` gives the only one instance of program arguments.

May actually be a :class:`._scenarioargs.ScenarioArgs` or a :class:`._campaignargs.CampaignArgs` instance,
or whatever subclass of :class:`Args`,
depending on the instance installed with :meth:`Args.setinstance()`.
"""

import argparse
import typing

from ._configargs import CommonConfigArgs  # `CommonConfigArgs` used for inheritance.
from ._logger import Logger  # `Logger` used for inheritance.
from ._loggingargs import CommonLoggingArgs  # `CommonLoggingArgs` used for inheritance.


class Args(Logger, CommonConfigArgs, CommonLoggingArgs):
    """
    Common program arguments management.

    Handles:

    - ``--help`` option,
    - Configuration file options (see :class:`._configargs.CommonConfigArgs`),
    - Logging options (see :class:`._loggingargs.CommonLoggingArgs`).
    """

    #: Main instance of :class:`Args`.
    _instance = None  # type: typing.Optional[Args]

    @staticmethod
    def setinstance(
            instance,  # type: Args
            warn_reset=True,  # type: bool
    ):  # type: (...) -> None
        """
        Sets the main instance of :class:`Args`.

        :param instance: :class:`Args` instance.
        :param warn_reset: Set to ``False`` in order to avoid the warning to be logged.

        When consecutive calls occur, the latest overwrites the previous,
        and a warning is displayed unless ``warn_reset`` is set to ``False``.
        """
        from ._loggermain import MAIN_LOGGER

        if Args._instance and (instance is not Args._instance) and warn_reset:
            MAIN_LOGGER.warning(f"Multiple instances of argument parser: {instance!r} takes place of {Args._instance!r}")
        Args._instance = instance

    @classmethod
    def getinstance(
            cls,  # type: typing.Type[VarArgsType]
    ):  # type: (...) -> VarArgsType
        """
        Singleton.

        :return: Main :class:`Args` instance.

        .. warning:: The main :class:`Args` instance is not created automatically by this method,
                     and should be set with :meth:`setinstance()` prior to any :meth:`getinstance()` call.
        """
        from ._reflection import qualname

        assert Args._instance is not None, f"No {qualname(cls)} instance available"
        assert isinstance(Args._instance, cls), f"Wrong type {qualname(type(Args._instance))}, {qualname(cls)} expected"
        return Args._instance

    @classmethod
    def isset(
            cls,  # type: typing.Type[VarArgsType]
    ):  # type: (...) -> bool
        """
        Checks whether the single instance of :class:`Args` is set and of the ``cls`` type.

        :param cls: Expected type.
        :return: ``True`` if the single :class:`Args` instance is of the given type, ``False`` otherwise.
        """
        return isinstance(Args._instance, cls)

    def __init__(
            self,
            class_debugging,  # type: bool
    ):  # type: (...) -> None
        """
        Defines common program arguments.

        :param class_debugging: See :class:`._loggingargs.CommonLoggingArgs`.
        """
        from ._debugclasses import DebugClass
        from ._errcodes import ErrorCode

        Logger.__init__(self, log_class=DebugClass.ARGS)

        # Initialize parsing members.
        # ===========================

        #: ``argparse`` parser object.
        #:
        #: Protected member, intentionally available to subclasses.
        self._arg_parser = argparse.ArgumentParser(add_help=False)  # type: argparse.ArgumentParser

        # Fix default `argparse` strings.
        def _fixgrouptitle(
                argparse_member_name,  # type: str
        ):  # type: (...) -> None
            """
            Capitalize group titles.

            :param argparse_member_name: Name of the ``self._arg_parser`` member defining the group to fix the title for.
            """
            if hasattr(self._arg_parser, argparse_member_name):
                _group = getattr(self._arg_parser, argparse_member_name)  # type: typing.Any  ## Type `argparse._ArgumentGroup` not available.
                if hasattr(_group, "title") and isinstance(_group.title, str):
                    _group.title = _group.title.capitalize()
        _fixgrouptitle(argparse_member_name="_positionals")
        _fixgrouptitle(argparse_member_name="_optionals")

        #: ``argparse`` parsed arguments opaque result.
        #:
        #: Protected member, intentionally available to subclasses.
        self._args = None  # type: typing.Any

        #: Argument parsing error code.
        #:
        #: Public member, intentionally available to all.
        self.error_code = ErrorCode.ARGUMENTS_ERROR  # type: ErrorCode

        # Define program arguments.
        # =========================

        #: Help argument group.
        #:
        #: Protected member, intentionally available to subclasses.
        self._help_group = self._arg_parser.add_argument_group("Help")

        self._help_group.add_argument(
            "-h", "--help",
            action="help",
            help="Show this help message and exit.",
        )

        # Memo: Logging before configuration arguments.
        CommonLoggingArgs.__init__(self, class_debugging=class_debugging)
        CommonConfigArgs.__init__(self)

    def setprog(
            self,
            name,  # type: str
    ):  # type: (...) -> None
        """
        Overwrites program name.

        :param name: Program name to be displayed with usage info.
        """
        self._arg_parser.prog = name

    def setdescription(
            self,
            description,  # type: str
    ):  # type: (...) -> None
        """
        Overwrites program description.

        :param description: Program description to be displayed with usage info.
        """
        self._arg_parser.description = description

    def parse(
            self,
            args,  # type: typing.Sequence[str]
    ):  # type: (...) -> bool
        """
        Parses program arguments.

        :param args: Argument list, without the program name.
        :return: ``True`` for success, ``False`` otherwise.
        """
        from ._configdb import CONFIG_DB
        from ._errcodes import ErrorCode
        from ._loggermain import MAIN_LOGGER
        from ._path import Path

        # Parse command line arguments.
        self._args = self._arg_parser.parse_args(args)

        try:
            # Load configurations:
            # - 1) load the single configuration values so that they are taken into account immediately,
            for _key in self.config_values:  # type: str
                CONFIG_DB.set(_key, data=self.config_values[_key], origin="<args>")
            # - 2) load configuration files,
            for _config_path in self.config_paths:  # type: Path
                try:
                    CONFIG_DB.loadfile(_config_path)
                except EnvironmentError as _env_err:
                    self.error_code = ErrorCode.ENVIRONMENT_ERROR
                    raise _env_err
            # - 3) reload the single configuration values, so that they prevail on configuration files.
            for _key in self.config_values:  # Type already declared above.
                CONFIG_DB.set(_key, data=self.config_values[_key], origin="<args>")
        except Exception as _err:
            MAIN_LOGGER.error(str(_err))
            self._args = None  # Invalidate argument parsing.
            return False

        # Configure unclassed debugging.
        MAIN_LOGGER.enabledebug(self.debug_main)

        # Post-check arguments.
        if not self._checkargs():
            self._arg_parser.print_usage()
            self._args = None  # Invalidate argument parsing.
            return False

        self.error_code = ErrorCode.SUCCESS
        return True

    @property
    def parsed(self):  # type: () -> bool
        """
        Parsed flag.
        Tells whether arguments have been successfully parsed yet or not.
        """
        return self._args is not None

    def _checkargs(self):  # type: (...) -> bool
        """
        Handler for special verifications on program arguments.

        :return: ``True`` for success, ``False`` otherwise.

        Shall be overridden in subclasses.
        """
        return True


if typing.TYPE_CHECKING:
    #: Variable `Args` type.
    #:
    #: Makes it possible to define class methods that return an instance of subclasses.
    VarArgsType = typing.TypeVar("VarArgsType", bound=Args)
