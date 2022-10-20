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
Log handling.
"""

import logging
import typing


class LogHandler:
    """
    Log handler management.
    """

    #: Console handler instance.
    #:
    #: Created with the main logger.
    console_handler = None  # type: typing.Optional[logging.StreamHandler]

    #: File handler instance, when started.
    #:
    #: Created when the logging service is started and file logging is required.
    file_handler = None  # type: typing.Optional[logging.FileHandler]
