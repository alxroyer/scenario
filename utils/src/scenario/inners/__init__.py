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

# Reexports.
try:
    # Memo:
    #   Module reexports with renamings are not considered as reexports when imported from `scenario` (and not '.' probably? tbc).
    #   Let's reexport them through intermediate shortcut variables.
    from scenario import _reflection as _reflection  # noqa  ## Access to a protected member
    reflection = _reflection
    from scenario import _textutils as _textutils  # noqa  ## Access to a protected member
    textutils = _textutils
    from scenario._fastpath import FAST_PATH as FAST_PATH  # noqa  ## Access to a protected member
finally:
    pass
