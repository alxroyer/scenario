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

import logging
import typing


def sphinxlogger():  # type: (...) -> logging.Logger
    return logging.getLogger("sphinx")


class SphinxLogger:

    def __init__(
            self,
            log_class,  # type: str
            enable_debug,  # type: bool
    ):  # type: (...) -> None
        self.log_class = log_class  # type: str
        self.enable_debug = enable_debug  # type: bool

    def debug(
            self,
            fmt,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        if self.enable_debug:
            sphinxlogger().debug(f"[scenario.tools.sphinx:%s] {fmt}", self.log_class, *args)

    def info(
            self,
            msg,  # type: str
    ):  # type: (...) -> None
        self.debug("INFO: %s", msg)
        sphinxlogger().info(msg)

    def warning(
            self,
            msg,  # type: str
    ):  # type: (...) -> None
        self.debug("WARNING: %s", msg)
        sphinxlogger().warning(f"WARNING: {msg}")
