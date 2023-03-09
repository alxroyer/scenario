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
:class:`SubProcess` class definition.
"""

import logging
import os
import pathlib
import subprocess
import sys
import threading
import typing

if typing.TYPE_CHECKING:
    from ._errcodes import ErrorCode as _ErrorCodeType
    from ._logger import Logger as _LoggerType
    from ._path import AnyPathType


class SubProcess:
    """
    Sub-process execution.
    """
    def __init__(
            self,
            *args  # type: typing.Union[str, AnyPathType]
    ):  # type: (...) -> None
        """
        :param args:
            Command line arguments.
            May be the first arguments only, then rely on the :meth:`addargs()` method to add others.
        """
        from ._path import Path
        from ._stats import TimeStats

        #: Sub-process command line arguments.
        #:
        #: See :meth:`addargs()`.
        self.cmd_line = list(args)  # type: typing.List[typing.Union[str, AnyPathType]]
        #: See :meth:`setenv()`.
        self.env = {}  # type: typing.Dict[str, typing.Union[str, AnyPathType]]
        #: See :meth:`setcwd()`.
        self.cwd = None  # type: typing.Optional[Path]

        #: See :meth:`setlogger()`.
        self._logger = None  # type: typing.Optional[_LoggerType]
        #: Handler to call on each stdout line.
        self._stdout_line_handler = None  # type: typing.Optional[typing.Callable[[bytes], None]]
        #: Handler to call on each stderr line.
        self._stderr_line_handler = None  # type: typing.Optional[typing.Callable[[bytes], None]]
        #: See :meth:`exitonerror()`.
        self._exit_on_error_code = None  # type: typing.Optional[_ErrorCodeType]

        #: Sub-process return code.
        self.returncode = None  # type: typing.Optional[int]
        #: Standard output as a string.
        self.stdout = b''  # type: bytes
        #: Standard error as a string.
        self.stderr = b''  # type: bytes
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats

        #: :class:`subprocess.Popen` instance.
        self._popen = None  # type: typing.Optional[subprocess.Popen[bytes]]
        #: Tells whether the :meth:`run()` method should wait for the end of the sub-process.
        self._async = False  # type: bool
        #: Stdout reader thread routine.
        self._stdout_reader = None  # type: typing.Optional[threading.Thread]
        #: Stderr reader thread routine.
        self._stderr_reader = None  # type: typing.Optional[threading.Thread]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflex import qualname

        return f"{qualname(type(self))}({self.cmd_line!r}, cwd={self.cwd!r}, env={self.env!r})"

    def __str__(self):  # type: () -> str
        """
        Human readable string representation.
        """
        _str = self.tolongstring()[2:-1]  # type: str
        if len(_str) > 64 - 3:
            _str = _str[:64-3] + "..."
        return f"$({_str})"

    def tolongstring(self):  # type: (...) -> str
        """
        Human readable full string representation.
        """
        _args = [str(_arg) for _arg in self.cmd_line]  # type: typing.List[str]

        # When the first term of the command line is the python executable,
        # ensure a short display for it.
        if _args and (_args[0] == sys.executable):
            _args[0] = "python"

        return f"$({' '.join(_args)})"

    def addargs(
            self,  # type: VarSubProcessType
            *args  # type: typing.Union[str, AnyPathType]
    ):  # type: (...) -> VarSubProcessType
        """
        Extra arguments addition.

        :param args: Extra arguments.
        :return: ``self``
        """
        self.cmd_line.extend(args)
        return self

    def hasargs(
            self,
            *args  # type: typing.Union[str, AnyPathType]
    ):  # type: (...) -> bool
        """
        Determines whether the command line contains the given sequence of consecutive arguments.

        :param args: Sequence of arguments being searched.
        :return: ``True`` when the arguments have been found, ``False`` otherwise.
        """
        _arg_index1 = 0  # type: int
        while _arg_index1 + len(args) - 1 < len(self.cmd_line):
            _arg_index2 = 0  # type: int
            while True:
                if _arg_index2 >= len(args):
                    return True
                if self.cmd_line[_arg_index1 + _arg_index2] != args[_arg_index2]:
                    _arg_index1 += 1
                    break
                else:
                    _arg_index2 += 1
        return False

    def setenv(
            self,  # type: VarSubProcessType
            **kwargs  # type: typing.Union[str, AnyPathType]
    ):  # type: (...) -> VarSubProcessType
        """
        Sets extra environment variables.

        :param kwargs: Extra environment variables.
        :return: ``self``
        """
        self.env.update(**kwargs)
        return self

    def setcwd(
            self,  # type: VarSubProcessType
            cwd,  # type: AnyPathType
    ):  # type: (...) -> VarSubProcessType
        """
        Sets the current working directory.

        :param cwd: Current working directory.
        :return: ``self``
        """
        from ._path import Path

        self.cwd = Path(cwd)
        return self

    def setlogger(
            self,  # type: VarSubProcessType
            logger,  # type: _LoggerType
    ):  # type: (...) -> VarSubProcessType
        """
        Directs log lines to the given logger instance.

        :param logger: Logger instance to use.
        :return: `` self``
        """
        self._logger = logger
        return self

    def onstdoutline(
            self,  # type: VarSubProcessType
            handler,  # type: typing.Callable[[bytes], None]
    ):  # type: (...) -> VarSubProcessType
        """
        Installs a handler to be called on each stdout line.

        :param handler: Handler to call on each stdout line.
        :return: ``self``
        """
        self._stdout_line_handler = handler
        return self

    def onstderrline(
            self,  # type: VarSubProcessType
            handler,  # type: typing.Callable[[bytes], None]
    ):  # type: (...) -> VarSubProcessType
        """
        Installs a handler to be called on each stderr line.

        :param handler: Handler to call on each stderr line.
        :return: ``self``
        """
        self._stderr_line_handler = handler
        return self

    def exitonerror(
            self,  # type: VarSubProcessType
            exit_on_error_code,  # type: typing.Union[bool, typing.Optional[_ErrorCodeType]]
    ):  # type: (...) -> VarSubProcessType
        """
        Tells whether the main program should stop (``sys.exit()``) in case of an error.

        :param exit_on_error_code:
            Set to ``None`` to keep executing in case of an error (default behaviour).
            Set to a :class:`.errcodes.ErrorCode` value to make the main program stop with the given error code.
            ``True`` is an equivalent for :const:`.errcodes.ErrorCode.INTERNAL_ERROR`,
            ``False`` is an equivalent for ``None``.
        :return: ``self``

        The return code is available through the :attr:`returncode` attribute.
        """
        from ._errcodes import ErrorCode

        if isinstance(exit_on_error_code, bool):
            self._exit_on_error_code = ErrorCode.INTERNAL_ERROR if exit_on_error_code else None
        else:
            self._exit_on_error_code = exit_on_error_code
        return self

    def run(
            self,  # type: VarSubProcessType
            timeout=None,  # type: float
    ):  # type: (...) -> VarSubProcessType
        """
        Sub-process execution.

        :param timeout: Waiting timeout, in seconds.``None`` to wait infinitely.
        :return: ``self``

        The sub-process return code is available through the :attr:`returncode` attribute.
        """
        if self._async:
            self._log(logging.DEBUG, "Launching %s", self.tolongstring())
        else:
            self._log(logging.DEBUG, "Executing %s", self.tolongstring())

        # Prepare the current working directory.
        _cwd = pathlib.Path.cwd()  # type: AnyPathType
        if self.cwd:
            self._log(logging.DEBUG, "  cwd: '%s'", self.cwd)
            _cwd = self.cwd

        # Prepare the command line arguments.
        _cmd_line = []  # type: typing.List[str]
        for _arg in self.cmd_line:  # type: typing.Union[str, AnyPathType]
            if isinstance(_arg, os.PathLike):
                # Use relative paths to ``_cwd`` when applicable.
                _path = pathlib.Path(_arg)  # type: pathlib.Path
                # Note: :meth:`pathlib.PurePath.is_relative_to()` available in Python 3.9 only.
                #       That's the reason why we use `startswith()` below.
                if _path.is_absolute() and os.fspath(_path).startswith(os.fspath(_cwd)):
                    _cmd_line.append(os.fspath(_path.relative_to(_cwd)))
                else:
                    _cmd_line.append(os.fspath(_arg))
            else:
                _cmd_line.append(_arg)

        # Prepare environment variables.
        _env = os.environ.copy()  # type: typing.Dict[str, str]
        if self.env:
            self._log(logging.DEBUG, "  additional env: %r", self.env)
            for _var in self.env:  # type: str
                if isinstance(self.env[_var], os.PathLike):
                    _env[_var] = os.fspath(self.env[_var])
                else:
                    _env[_var] = str(self.env[_var])

        # Launch the subprocess.
        self.time.setstarttime()
        self.returncode = None
        try:
            self._popen = subprocess.Popen(
                _cmd_line, cwd=_cwd, env=_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as _err:
            self._onerror("Error while executing %s: %s", self, _err)
            return self

        # Launch the stdout and stderr reader threads.
        self._stdout_reader = threading.Thread(name=f"{self}[stdout]", target=self._readstdoutthread)
        self._stdout_reader.start()
        self._stderr_reader = threading.Thread(name=f"{self}[stderr]", target=self._readstderrthread)
        self._stderr_reader.start()

        # Wait for the end of the sub-process.
        if not self._async:
            try:
                self.wait(timeout=timeout)
            except TimeoutError as _err:
                self._popen.kill()
                self._onerror("%s timeout: %s", self, _err)

        return self

    def runasync(
            self,  # type: VarSubProcessType
    ):  # type: (...) -> VarSubProcessType
        """
        Launches the sub-process asynchronously.

        Contrary to :meth:`run()`,
        this method launches the sub-process, then returns without waiting for the end of it.
        """
        self._async = True
        return self.run()

    def _readstdoutthread(self):  # type: (...) -> None
        """
        Stdout reader thread routine.
        """
        while self._popen and self._popen.stdout:
            # Read a stdout line.
            _line = self._popen.stdout.readline()  # type: bytes
            if not _line:
                break

            # Save it in the stdout buffer as is, then remove the end-of-line character(s).
            self.stdout += _line
            _line = _line.rstrip(b'\r\n')

            # Debug the line (only if no stdout handler is set).
            if not self._stdout_line_handler:
                self._log(logging.DEBUG, "  stdout: %r", _line)

            # Call the user handler.
            if self._stdout_line_handler:
                # Prevent from potential exceptions in the user handler.
                try:
                    self._stdout_line_handler(_line)
                except Exception as _err:
                    self._log(logging.ERROR, str(_err))

    def _readstderrthread(self):  # type: (...) -> None
        """
        Stderr reader thread routine.
        """
        while self._popen and self._popen.stderr:
            # Read a stderr line.
            _line = self._popen.stderr.readline()  # type: bytes
            if not _line:
                break

            # Save it in the stderr buffer as is, then remove the end-of-line character(s).
            self.stderr += _line
            _line = _line.rstrip(b'\r\n')

            # Debug the line (only if no stderr handler is set).
            if not self._stderr_line_handler:
                self._log(logging.DEBUG, "  stderr: %r", _line)

            # Call the user handler.
            if self._stderr_line_handler:
                # Prevent from potential exceptions in the user handler.
                try:
                    self._stderr_line_handler(_line)
                except Exception as _err:
                    self._log(logging.ERROR, str(_err))

    def isrunning(self):  # type: (...) -> bool
        """
        Tells whether the sub-process is currently running.

        :return: ``True`` when the sub-process is still running. ``False`` otherwise.
        """
        if self._popen:
            return self._popen.poll() is None
        return False

    def wait(
            self,  # type: VarSubProcessType
            timeout=None,  # type: float
    ):  # type: (...) -> VarSubProcessType
        """
        Waits for the sub-process to terminate.

        :param timeout: Waiting timeout, in seconds. ``None`` to wait infinitely.
        :return: ``self``
        :raise TimeoutError: When the sub-process did not terminate within ``timeout`` seconds.
        """
        from ._debugutils import saferepr

        if not self._popen:
            raise ValueError(f"{self}: Cannot wait before the process is created")
        try:
            if timeout is not None:
                self._log(logging.DEBUG, "Waiting for %s to terminate within %f seconds", self.tolongstring(), timeout)
            else:
                self._log(logging.DEBUG, "Waiting for %s to terminate...", self.tolongstring())
            self.returncode = self._popen.wait(timeout=timeout)
        except subprocess.TimeoutExpired as _err:
            raise TimeoutError(str(_err))

        self.time.setendtime()

        if self._stdout_reader:
            self._stdout_reader.join()
        if self._stderr_reader:
            self._stderr_reader.join()

        if self.returncode != 0:
            self._onerror("%s failed: retcode=%r, stderr=%s", self.tolongstring(), self.returncode, saferepr(self.stderr))

        return self

    def kill(
            self,  # type: VarSubProcessType
    ):  # type: (...) -> VarSubProcessType
        """
        Kills the sub-process.

        :return: ``self``
        """
        if self._popen:
            self._popen.kill()

        if self._stdout_reader:
            self._stdout_reader.join()
        if self._stderr_reader:
            self._stderr_reader.join()

        return self

    def _onerror(
            self,
            error_message,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        """
        Error management.

        Optionally logs the error and terminates the main process.

        :param error_message: Error message.
        :param args: Error message arguments.
        """
        # Optionally log the error, i.e. when the main process will be stopped.
        if self._exit_on_error_code is not None:
            self._log(logging.ERROR, error_message, *args)

        # Optionally terminate the main process.
        if self._exit_on_error_code is not None:
            sys.exit(int(self._exit_on_error_code))

    def _log(
            self,
            level,  # type: int
            message,  # type: str
            *args,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Pushes a log line to the attached logger, if any.

        :param level: Log level.
        :param message: Log message.
        :param args: Format arguments.
        """
        if self._logger:
            self._logger.log(level, message, *args)


if typing.TYPE_CHECKING:
    #: Variable subprocess type.
    VarSubProcessType = typing.TypeVar("VarSubProcessType", bound=SubProcess)
