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
This subpackage makes a couple of inner :mod:`scenario` symbols available for :mod:`scenario.test`, :mod:`scenario.tools`, ...
"""

import typing


# Reexports.
try:
    # Explicit export declarations (see https://docs.python.org/3/tutorial/modules.html#importing-from-a-package).
    __all__ = []  # type: typing.List[str]

    from scenario import _perfutils as perfutils
    __all__.append("perfutils")
    from scenario import _textfileutils as textfileutils
    __all__.append("textfileutils")
    from scenario import _textutils as textutils
    __all__.append("textutils")
    from scenario._fastpath import FAST_PATH as FAST_PATH  # noqa  ## Access to a protected member
    __all__.append("FAST_PATH")
    from scenario._jsondictutils import JsonDict as JsonDict  # noqa  ## Access to a protected member
    __all__.append("JsonDict")
    from scenario._reflection import REFLECTION as reflection  # noqa  ## Access to a protected member + Constant variable imported as non-constant
    __all__.append("reflection")
finally:
    pass
