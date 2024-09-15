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

import scenario


def setdefaulttestsuites():  # type: (...) -> None
    """
    Sets :attr:`._paths.TEST_SUITE_FILES` as the default test suite files.
    """
    from . import _paths as _paths

    scenario.conf.remove(scenario.ConfigKey.TEST_SUITE_FILES)
    scenario.conf.set(scenario.ConfigKey.TEST_SUITE_FILES, [_path.abspath for _path in _paths.TEST_SUITE_FILES])
