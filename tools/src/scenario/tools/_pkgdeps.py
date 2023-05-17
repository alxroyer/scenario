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


def checkpkgdeps():  # type: (...) -> None
    from ._paths import MAIN_PATH

    # Ensure `scenario.text` can be loaded.
    try:
        import scenario.text
    except ImportError:
        # If not, extend the `scenario` namespace path list.
        import scenario
        scenario.__path__.append((MAIN_PATH / "utils" / "src" / "scenario").abspath)
        import scenario.text
