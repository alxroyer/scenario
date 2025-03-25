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
    from ._logextradata import LogExtraData as _LogExtraDataImpl  # @perf
    from ._logfilters import HandlerLogFilter as _HandlerLogFilterImpl  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._loghandler import LogHandler as _LogHandlerImpl  # @perf


class MainLogger(_LoggerImpl):
    """
    Main logger augmentation of :class:`._logger.Logger`.

    Shall be used for actions/results indentation (see :ref:`logging.indentation.action-result`).

    Instantiated once with the :data:`MAIN_LOGGER` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Enables debugging by default and makes console initializations.
        """
        from ._consoleutils import disableconsolebuffering  # check-imports: ignore  ## Once only import, no need to optimize.
        from ._logformatter import LogFormatter

        _LoggerImpl.__init__(self, log_class="")

        # Enable main logger debugging by default.
        self.enabledebug(True)

        # Ensure console configuration while creating the main logger.
        disableconsolebuffering()

        # Install the console handler (with its attached filter and formatter).
        #
        # Note:
        # A second dummy main logger may be instantiated due to our `scenario.tools.sphinx` implementation with `typing.TYPE_CHECKING` enabled.
        # Skip the console handler installation in that case.
        assert (_LogHandlerImpl.console_handler is None) or typing.TYPE_CHECKING, "Console handler already installed"
        if _LogHandlerImpl.console_handler is None:
            _LogHandlerImpl.console_handler = logging.StreamHandler()
            _LogHandlerImpl.console_handler.stream = sys.stdout  # Note: :meth:`logging.StreamHandler.setStream()` is not available in all Python versions.
            _LogHandlerImpl.console_handler.addFilter(_HandlerLogFilterImpl(handler=_LogHandlerImpl.console_handler))
            _LogHandlerImpl.console_handler.setFormatter(LogFormatter(_LogHandlerImpl.console_handler))
            self._logger.addHandler(_LogHandlerImpl.console_handler)

    def rawoutput(
            self,
            message,  # type: str
    ):  # type: (...) -> None
        """
        Logs a line with automatic formattings disabled.

        Helper function for the :class:`._scenariologging.ScenarioLogging` and :class:`._campaignlogging.CampaignLogging` classes.

        :param message: Log message to output.
        """
        self.info(
            message,
            extra={
                _LogExtraDataImpl.LOG_LEVEL: False,
                _LogExtraDataImpl.COLOR: False,
                _LogExtraDataImpl.MAIN_LOGGER_INDENTATION: False,
                _LogExtraDataImpl.ACTION_RESULT_MARGIN: False,
            },
        )


#: Main logger instance.
#:
#: Also available as :attr:`._fastpath.FastPath.main_logger`.
#: Please prefer the latter instead of using local imports of this module.
MAIN_LOGGER = MainLogger()  # type: MainLogger
