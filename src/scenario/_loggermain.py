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
:class:`MainLogger` class definition
with :data:`MAIN_LOGGER` singleton.
"""

import logging
import sys
import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.


class MainLogger(_LoggerImpl):
    """
    Main logger augmentation of :class:`._logger.Logger`.

    Instantiated once with the :data:`MAIN_LOGGER` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Enables debugging by default and makes console initializations.
        """
        from ._consoleutils import disableconsolebuffering
        from ._logfilters import HandlerLogFilter
        from ._logformatter import LogFormatter
        from ._loghandler import LogHandler

        _LoggerImpl.__init__(self, log_class="")

        # Enable main logger debugging by default.
        self.enabledebug(True)

        # Ensure console configuration while creating the main logger.
        disableconsolebuffering()

        # Install the console handler (with its attached filter and formatter).
        #
        # Note:
        # A second dummy main logger may be instanciated due to our `scenario.tools.sphinx` implementation with `typing.TYPE_CHECKING` enabled.
        # Skip the console handler installation in that case.
        assert (LogHandler.console_handler is None) or typing.TYPE_CHECKING, "Console handler already installed"
        if LogHandler.console_handler is None:
            LogHandler.console_handler = logging.StreamHandler()
            LogHandler.console_handler.stream = sys.stdout  # Note: :meth:`logging.StreamHandler.setStream()` is not available in all Python versions.
            LogHandler.console_handler.addFilter(HandlerLogFilter(handler=LogHandler.console_handler))
            LogHandler.console_handler.setFormatter(LogFormatter(LogHandler.console_handler))
            self._logger.addHandler(LogHandler.console_handler)

    def rawoutput(
            self,
            message,  # type: str
    ):  # type: (...) -> None
        """
        Logs a line with automatic formattings disabled.

        Helper function for the :class:`._scenariologging.ScenarioLogging` and :class:`._campaignlogging.CampaignLogging` classes.

        :param message: Log message to output.
        """
        from ._logextradata import LogExtraData

        self.info(
            message,
            extra=LogExtraData.extradata({
                LogExtraData.LOG_LEVEL: False,
                LogExtraData.COLOR: False,
                LogExtraData.MAIN_LOGGER_INDENTATION: False,
                LogExtraData.ACTION_RESULT_MARGIN: False,
            }),
        )


#: Main logger instance.
MAIN_LOGGER = MainLogger()  # type: MainLogger
