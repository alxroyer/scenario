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
User interface launching.
"""

import sys
import typing

if typing.TYPE_CHECKING:
    from .._errcodes import ErrorCode as _ErrorCodeType


def main():  # type: (...) -> _ErrorCodeType
    """
    User interface launcher function.

    :return: Error code.
    """
    from .._args import Args
    from .._campaigndb import CAMPAIGN_DB
    from .._errcodes import ErrorCode
    from .._loggermain import MAIN_LOGGER
    from .._loggingservice import LOGGING_SERVICE
    from .._reqtraceability import REQ_TRACEABILITY
    from ._httpserver import HTTP_SERVER

    # Analyze program arguments, if not already set.
    if not Args.isset():
        Args.setinstance(Args(class_debugging=True))
        if not Args.getinstance().parse(sys.argv[1:]):
            return Args.getinstance().error_code

    # Start log features.
    LOGGING_SERVICE.start()

    try:
        # Load default requirements and scenarios from `ScenarioConfig.Key.REQ_DB_FILES` and `TEST_SUITE_FILES` configurations.
        REQ_TRACEABILITY.loaddatafromfiles()
        # Load campaign results.
        CAMPAIGN_DB.load()

        # Launch the HTTP server.
        MAIN_LOGGER.info("")
        HTTP_SERVER.serve()
    except Exception as _err:
        MAIN_LOGGER.logexceptiontraceback(_err)
        return ErrorCode.fromexception(_err)

    # Terminate log features.
    LOGGING_SERVICE.stop()

    return ErrorCode.SUCCESS
