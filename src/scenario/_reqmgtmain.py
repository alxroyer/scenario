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
Requirement management main program.
"""

import logging
import sys
import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._errcodes import ErrorCode as _ErrorCodeType


class ReqManagement(_LoggerImpl):

    def __init__(self):  # type: (...) -> None
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_MANAGEMENT)

    def main(self):  # type: (...) -> _ErrorCodeType
        from ._errcodes import ErrorCode
        from ._loggermain import MAIN_LOGGER
        from ._loggingservice import LOGGING_SERVICE
        from ._reqhttpserver import REQ_HTTP_SERVER
        from ._reqmgtargs import ReqManagementArgs
        from ._reqtraceability import REQ_TRACEABILITY
        from ._testerrors import ExceptionError

        # Analyze program arguments, if not already set.
        if not ReqManagementArgs.isset():
            ReqManagementArgs.setinstance(ReqManagementArgs())
            if not ReqManagementArgs.getinstance().parse(sys.argv[1:]):
                return ReqManagementArgs.getinstance().error_code

        # Start log features.
        LOGGING_SERVICE.start()

        _errors = []  # type: typing.List[ErrorCode]

        # Requirement & scenario loading.
        try:
            REQ_TRACEABILITY.loaddata(
            )
        except Exception as _err:
            ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
            _errors.append(ErrorCode.fromexception(_err))

        # Execute `ReqManagementArgs` options.
        if not _errors:
            # Downstream traceability report.
            if not ReqManagementArgs.getinstance().downstream_traceability_outfile.is_void():
                try:
                    REQ_TRACEABILITY.writedownstream(
                        downstream_traceability=REQ_TRACEABILITY.getdownstream(),
                        outfile=ReqManagementArgs.getinstance().downstream_traceability_outfile,
                    )
                except Exception as _err:
                    ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
                    _errors.append(ErrorCode.fromexception(_err))

            # Upstream traceability report.
            if not ReqManagementArgs.getinstance().upstream_traceability_outfile.is_void():
                try:
                    REQ_TRACEABILITY.writeupstream(
                        upstream_traceability=REQ_TRACEABILITY.getupstream(),
                        outfile=ReqManagementArgs.getinstance().upstream_traceability_outfile,
                    )
                except Exception as _err:
                    ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
                    _errors.append(ErrorCode.fromexception(_err))

            # HTTP server.
            if ReqManagementArgs.getinstance().serve:
                try:
                    REQ_HTTP_SERVER.serve()
                except InterruptedError as _err:
                    self.debug("InterruptedError: %s", _err)
                except Exception as _err:
                    ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
                    _errors.append(ErrorCode.fromexception(_err))

        # Terminate log features.
        LOGGING_SERVICE.stop()

        # End.
        return ErrorCode.worst(_errors)


REQ_MANAGEMENT = ReqManagement()  # type: ReqManagement
