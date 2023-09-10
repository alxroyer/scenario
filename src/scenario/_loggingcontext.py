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
Logging contexts.
"""

import typing

if typing.TYPE_CHECKING:
    from ._logger import Logger as _LoggerType


class LoggingContext:
    """
    Logging context.

    Controls the way logging is done for a ``with`` block.
    """

    def __init__(
            self,
            logger,  # type: _LoggerType
            indentation="",  # type: str
    ):  # type: (...) -> None
        """
        :param logger: Logger reference that the context works on.
        :param indentation: Indentation to push for the given logger.
        """
        #: Logger reference that the context works on.
        self.logger = logger  # type: _LoggerType
        #: Indentation to push for the given logger.
        self.indentation = indentation  # type: str

        #: Flag that saves whether the context is already on or not.
        #:
        #: Flag required for hacks like in :meth:`._logger.Logger.pushindentation()`.
        self._active = False  # type: bool

    def __enter__(self):  # type: (...) -> None
        """
        Beginning of context.
        """
        if not self._active:
            self._active = True

            if self.indentation:
                self.logger.pushindentation(indentation=self.indentation)

    def __exit__(
            self,
            exc_type,  # type: typing.Any
            exc_val,  # type: typing.Any
            exc_tb,  # type: typing.Any
    ):  # type: (...) -> None
        """
        End of context.
        """
        if self._active:
            self._active = False

            if self.indentation:
                self.logger.popindentation(indentation=self.indentation)
