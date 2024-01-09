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
No-dependency module that makes data available without importing other modules.

Avoids cyclic module dependencies, and numerous local imports in the same time.

Nevertheless, usage of this global data approach shall be reserved when performance issues are revealed,
and justified in the related data docstring.
"""

import typing

if typing.TYPE_CHECKING:
    from ._args import Args as _ArgsType


class FastPath:
    """
    Fast path data container.
    """

    def __init__(self):  # type: (...) -> None
        """
        Declares fast path data.
        """
        #: :class:`._args.Args` instance installed.
        #:
        #: Making this information global avoids numerous local imports,
        #: especially for logging management.
        self.args = None  # type: typing.Optional[_ArgsType]


#: Main instance of :class:`FastPath`.
FAST_PATH = FastPath()
