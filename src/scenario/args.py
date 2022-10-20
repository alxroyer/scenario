# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

:meth:`Args.getinstance()` gives the only only instance of program arguments,
May actually be a :class:`.scenarioargs.ExecArgs` or a :class:`.campaignargs.CampaignArgs` instance.
"""

import argparse
import typing

# `Logger` used for inheritance.
from .logger import Logger


class Args(Logger):
    """
    Common program arguments management.

    Handles:

    - ``--help`` option,
    - Configuration file options,
    - Logging options.
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
        :param warn_reset: Set to :const:`False` in order to avoid the warning to be logged.

        When consecutive calls occur, the latest overwrites the previous,
        and a warning is displayed unless ``warn_reset`` is set to :const:`False`.
        """
        from .loggermain import MAIN_LOGGER

        if Args._instance and (instance is not Args._instance) and warn_reset:
            MAIN_LOGGER.warning("Multiple instances of argument parser: %s takes place of %s" % (repr(instance), repr(Args._instance)))
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
        from .reflex import qualname

        assert Args._instance is not None, "No %s instance available" % qualname(cls)
        assert isinstance(Args._instance, cls), "Wrong type %s, %s expected" % (qualname(type(Args._instance)), qualname(cls))
        return Args._instance

    @classmethod
    def isset(
            cls,  # type: typing.Type[VarArgsType]
    ):  # type: (...) -> bool
        """
        Checks whether the single instance of :class:`Args` is set and of the ``cls`` type.

        :param cls: Expected type.
        :return: :const:`True` if the single :class:`Args` instance is of the given type, :const:`False` otherwise.
        """
        return isinstance(Args._instance, cls)

    def __init__(
            self,
            class_debugging,  # type: bool
    ):  # type: (...) -> None
        """
        Defines common program arguments.

        :param class_debugging: :const:`True` to enable per-class debugging.
                                :const:`False` for unclassed debugging only.

        When per-class debugging is enabled, the main logger debugging is enabled by default.
        """
        from .debug import DebugClass
        from .errcodes import ErrorCode
        from .path import Path

        Logger.__init__(self, log_class=DebugClass.ARGS)

        # Initialize parsing members.

        #: :mod:`argparse` parser object.
        self.__arg_parser = argparse.ArgumentParser(add_help=False)  # type: argparse.ArgumentParser

        #: Arguments information.
        self.__arg_infos = {}  # type: typing.Dict[str, ArgInfo]

        #: Parsed flag.
        #: Tells whether arguments have been successfully parsed yet or not.
        self.parsed = False

        #: Error code.
        self.error_code = ErrorCode.ARGUMENTS_ERROR  # type: ErrorCode

        # Common command line arguments.
        self.__arg_parser.add_argument(
            "-h", "--help",
            action="help",
            help="Show this help message and exit.",
        )

        #: Configuration files.
        self.config_paths = []  # type: typing.List[Path]
        self.addarg("Configuration files", "config_paths", Path).define(
            "--config-file", metavar="CONFIG_PATH",
            action="append", type=str, default=[],
            help="Input configuration file path. "
                 "This option may be called several times.",
        )
        #: Additional configuration values.
        self.config_values = {}  # type: typing.Dict[str, str]
        self.addarg("Configuration values", "config_values", (str, str)).define(
            "--config-value", metavar=("KEY", "VALUE"), nargs=2,
            action="append", type=str, default=[],
            help="Configuration value in the 'key=value' form. "
                 "This option may be called several times.",
        )

        #: Main logger debugging.
        self.debug_main = False  # type: bool
        if class_debugging:
            self.debug_main = True
        else:
            self.addarg("Debug main", "debug_main", bool).define(
                "--debug",
                action="store_true", default=False,
                help="Enable debugging.",
            )
        #: Debug classes activated.
        self.debug_classes = []  # type: typing.List[str]
        if class_debugging:
            self.addarg("Debug classes", "debug_classes", str).define(
                "--debug-class", metavar="DEBUG_CLASS",
                action="append", type=str, default=[],
                help="Activate debugging for the given class.",
            )

    def setprog(
            self,
            name,  # type: str
    ):  # type: (...) -> None
        """
        Overwrites program name.

        :param name: Program name to be displayed with usage info.
        """
        self.__arg_parser.prog = name

    def setdescription(
            self,
            description,  # type: str
    ):  # type: (...) -> None
        """
        Overwrites program description.

        :param description: Program description to be displayed with usage info.
        """
        self.__arg_parser.description = description

    def addarg(
            self,
            member_desc,  # type: str
            member_name,  # type: str
            member_type,  # type: typing.Union[type, typing.Tuple[typing.Type[str], type]]
    ):  # type: (...) -> ArgInfo
        """
        Adds a program argument.

        :param member_desc: Textual description of the program argument(s).
        :param member_name: Corresponding member name in the owner :class:`Args` instance.
        :param member_type: Type of the program argument, or base type of the program arguments list.
                            When defined as a 2 items tuple, the argument feeds a dictionary:
                            the first item of the tuple shall be ``str`` (for the dictionary keys),
                            and the second item gives the type of the dictionary values.
        :return: :class:`Args.ArgInfo` instance whose :meth:`ArgInfo.define()` should be called onto.

        :meth:`ArgInfo.define()` should be called on the :class:`ArgInfo` object returned:

        .. code-block:: python

           self.addarg("Configuration files", "config_paths", Path).define(
               "--config-file", metavar="CONFIG_PATH",
               action="append", type=str, default=[],
               help="Input configuration file path. "
                    "This option may be called several times.",
           )
        """
        self.__arg_infos[member_name] = ArgInfo(self.__arg_parser, member_desc, member_name, member_type)
        return self.__arg_infos[member_name]

    def parse(
            self,
            args,  # type: typing.List[str]
    ):  # type: (...) -> bool
        """
        Parses program arguments.

        :param args: Argument list, without the program name.
        :return: :const:`True` for success, :const:`False` otherwise.
        """
        from .configdb import CONFIG_DB
        from .errcodes import ErrorCode
        from .loggermain import MAIN_LOGGER
        from .path import Path

        # Parse command line arguments.
        _parsed_args = self.__arg_parser.parse_args(args)  # type: typing.Any

        # Copy arguments from the untyped `_parsed_args` object to `self`.
        for _member_name in self.__arg_infos:  # type: str
            if not self.__arg_infos[_member_name].process(self, _parsed_args):
                return False

        # Load configurations:
        # - 1) load the single configuration values so that they are taken in account immediately,
        for _key in self.config_values:  # type: str
            try:
                CONFIG_DB.set(_key, data=Args.getinstance().config_values[_key], origin="<args>")
            except Exception as _err:
                MAIN_LOGGER.error(str(_err))
                return False
        # - 2) load configuration files,
        for _config_path in self.config_paths:  # type: Path
            try:
                CONFIG_DB.loadfile(_config_path)
            except EnvironmentError as _env_err:
                self.error_code = ErrorCode.ENVIRONMENT_ERROR
                MAIN_LOGGER.error(str(_env_err))
                return False
            except Exception as _err:
                MAIN_LOGGER.error(str(_err))
                return False
        # - 3) reload the single configuration values, so that they prevail on configuration files.
        for _key in self.config_values:  # Type already declared above.
            try:
                CONFIG_DB.set(_key, data=Args.getinstance().config_values[_key], origin="<args>")
            except Exception as _err:
                MAIN_LOGGER.error(str(_err))
                return False

        # Configure unclassed debugging.
        MAIN_LOGGER.enabledebug(self.debug_main)

        # Post-check arguments.
        if not self._checkargs(_parsed_args):
            self.__arg_parser.print_usage()
            return False

        self.error_code = ErrorCode.SUCCESS
        self.parsed = True
        return True

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Handler for special verifications on program arguments.

        :param args: The untyped object returned by :meth:`argparse.ArgumentParser.parse_args()`.
        :return: :const:`True` for success, :const:`False` otherwise.

        Shall be overridden in subclasses.
        """
        return True


class ArgInfo:
    """
    Class that describes a single program argument (single value, list or dictionary).

    Whether the program argument is a single value, or a list of value, depends on the :mod:`argparse` definition made
    through :meth:`ArgInfo.define()`.
    """

    def __init__(
            self,
            arg_parser,  # type: argparse.ArgumentParser
            member_desc,  # type: str
            member_name,  # type: str
            member_type,  # type: typing.Union[type, typing.Tuple[typing.Type[str], type]]
    ):  # type: (...) -> None
        """
        :param arg_parser: Related :class:`argparse.ArgumentParser` instance.
        :param member_desc: Textual description of the program argument(s).
        :param member_name: Corresponding member name in the owner :class:`Args` instance.
        :param member_type: Base type of the program argument(s).
                            See :meth:`Args.addarg()` for a detailed description of this parameter.

        :meth:`Args.ArgInfo.define()` should be called onto each :class:`Args.ArgInfo` instance newly created.

        .. seealso:: :meth:`Args.addarg()`, :meth:`Args.ArgInfo.define()`
        """
        #: Related :class:`argparse.ArgumentParser` instance.
        self.arg_parser = arg_parser  # type: argparse.ArgumentParser
        #: Textual description of the program argument(s).
        self.member_desc = member_desc  # type: str
        #: Corresponding member name in the owner :class:`Args` instance.
        self.member_name = member_name  # type: str
        #: Key type, when the argument feeds a dictionary.
        self.key_type = None  # type: typing.Optional[typing.Type[str]]
        if isinstance(member_type, tuple):
            assert len(member_type) == 2
            self.key_type = member_type[0]
        #: Base type of the program argument(s).
        self.value_type = str  # type: type
        if isinstance(member_type, tuple):
            assert len(member_type) == 2
            self.value_type = member_type[1]
        else:
            self.value_type = member_type
        #: :class:`argparse.Action` instance defined by the :meth:`Args.ArgInfo.define()` method.
        self.parser_arg = None  # type: typing.Optional[argparse.Action]

    def define(
            self,
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Defines the :mod:`argparse` command line argument.

        :param args: List of positional arguments.
        :param kwargs: Dictionary of named arguments.

        Refer to the regular :mod:`argparse` documentation, except for the :attr:`dest` parameter which should not be set.
        The :attr:`Args.ArgInfo.member_name` member will be used for the purpose.

        Should be called on the :class:`Args.ArgInfo` returned the :meth:`Args.addarg()` method.

        .. seealso:: :meth:`Args.addarg()`
        """
        assert "dest" not in kwargs
        if len(args) > 0:
            self.arg_parser.add_argument(*args, dest=self.member_name, **kwargs)
        else:
            self.arg_parser.add_argument(self.member_name, **kwargs)

    def process(
            self,
            args_instance,  # type: Args
            parsed_args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Process the argument value once parsed by :mod:`argparse` and feed the :class:`Args` instance.

        :param args_instance: :class:`Args` instance to feed.
        :param parsed_args: Opaque parsed object returned by the :mod:`argparse` library.
        :return: :const:`True` when the operation succeeded, :const:`False` otherwise.
        """
        from .loggermain import MAIN_LOGGER
        from .path import Path
        from .reflex import qualname

        # Retrieve and check members from both: the :class:`Args` instance on the one hand, and the opaque parsed object on the other hand.
        if self.member_name not in vars(args_instance):
            MAIN_LOGGER.error("No such attribute '%s' in %s" % (self.member_name, qualname(type(args_instance))))
            return False
        _args_member = getattr(args_instance, self.member_name)  # type: typing.Any
        _parsed_member = getattr(parsed_args, self.member_name)  # type: typing.Any
        args_instance.debug("ArgInfo['%s'].process(): _parsed_member = %s" % (self.member_name, repr(_parsed_member)))
        if _parsed_member is None:
            # No value => nothing to do.
            # Things will be checked later on with the :meth:`Args._checkargs()` handler.
            return True
        if self.key_type is not None:
            if not isinstance(_args_member, dict):
                MAIN_LOGGER.error("Attribute '%s' in '%s' should be a dictionary" % (self.member_name, qualname(type(args_instance))))
                return False

        # Build the list of parsed values to process.
        _parsed_values = []  # type: typing.List[typing.Any]
        if isinstance(_parsed_member, list):
            _parsed_values.extend(_parsed_member)
        else:
            _parsed_values.append(_parsed_member)

        # Process each parsed value.
        for _parsed_value in _parsed_values:  # type: typing.Any
            # Parse the 'key=value' pattern for dictionary arguments.
            _parsed_key = ""  # type: str
            if self.key_type is not None:
                if (not isinstance(_parsed_value, list)) or (len(_parsed_value) != 2) or (not isinstance(_parsed_value[0], str)):
                    MAIN_LOGGER.error("%s should ba a [str, ANY] list" % repr(_parsed_value))
                    return False
                _parsed_key = _parsed_value[0]
                _parsed_value = _parsed_value[1]

            # Check and convert parsed item values.
            if (self.value_type is Path) and isinstance(_parsed_value, str):
                _parsed_value = Path(_parsed_value)
            if (_parsed_value is not None) and (not isinstance(_parsed_value, self.value_type)):
                MAIN_LOGGER.error("Wrong type %s, %s expected" % (repr(_parsed_value), self.value_type.__name__))
                return False

            # Save the value in the :class:`Args` instance.
            if self.key_type is not None:
                args_instance.debug("%s: %s: %s" % (self.member_desc, _parsed_key, repr(_parsed_value)))
                _args_member[_parsed_key] = _parsed_value
            elif isinstance(_args_member, list):
                args_instance.debug("%s: %d: %s" % (self.member_desc, len(_args_member), repr(_parsed_value)))
                _args_member.append(_parsed_value)
            else:
                args_instance.debug("%s: %s" % (self.member_desc, repr(_parsed_value)))
                setattr(args_instance, self.member_name, _parsed_value)

        return True


if typing.TYPE_CHECKING:
    VarArgsType = typing.TypeVar("VarArgsType", bound=Args)
