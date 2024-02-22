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

import sys
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._errcodes import ErrorCode as _ErrorCodeType
    from ._path import Path as _PathType


class ReqManagement(_LoggerImpl):
    """
    Requirement management main program.

    Instantiated once with the :data:`REQ_MANAGEMENT` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`ReqManagement` class.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_MANAGEMENT)

    def main(self):  # type: (...) -> _ErrorCodeType
        """
        Requirement management main function, as a member method.

        :return: Error code.
        """
        from ._errcodes import ErrorCode
        from ._loggingservice import LOGGING_SERVICE
        from ._reqmgtargs import ReqManagementArgs
        from ._reqtraceability import REQ_TRACEABILITY

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
            _campaign_results_path = ReqManagementArgs.getinstance().campaign_results_path  # type: typing.Optional[_PathType]
            if _campaign_results_path:
                REQ_TRACEABILITY.loaddatafromcampaignresults(_campaign_results_path)
            else:
                REQ_TRACEABILITY.loaddatafromfiles(
                    req_db_file_paths=ReqManagementArgs.getinstance().req_db_paths or None,
                    test_suite_paths=ReqManagementArgs.getinstance().test_suite_paths or None,
                )
        except Exception as _err:
            _FAST_PATH.main_logger.logexceptiontraceback(_err)
            _errors.append(ErrorCode.fromexception(_err))

        # Execute `ReqManagementArgs` options.
        if not _errors:
            # Downstream traceability report.
            _downstream_traceability_path = ReqManagementArgs.getinstance().downstream_traceability_outfile  # type: typing.Optional[_PathType]
            if _downstream_traceability_path:
                try:
                    REQ_TRACEABILITY.writedownstream(
                        _downstream_traceability_path,
                        allow_results=ReqManagementArgs.getinstance().allow_results,
                    )
                except Exception as _err:
                    _FAST_PATH.main_logger.logexceptiontraceback(_err)
                    _errors.append(ErrorCode.fromexception(_err))

            # Upstream traceability report.
            _upstream_traceability_path = ReqManagementArgs.getinstance().upstream_traceability_outfile  # type: typing.Optional[_PathType]
            if _upstream_traceability_path:
                try:
                    REQ_TRACEABILITY.writeupstream(
                        _upstream_traceability_path,
                    )
                except Exception as _err:
                    _FAST_PATH.main_logger.logexceptiontraceback(_err)
                    _errors.append(ErrorCode.fromexception(_err))

        # Terminate log features.
        LOGGING_SERVICE.stop()

        # End.
        return ErrorCode.worst(_errors)


#: Main instance of :class:`ReqManagement`.
REQ_MANAGEMENT = ReqManagement()  # type: ReqManagement
