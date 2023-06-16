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
    import scenario
    from scenario._reflection import extendnamespacepackagepath  # noqa  ## Access to protected member
    from ._paths import UTILS_SRC_PATH

    # Ensure `scenario.text` can be loaded.
    try:
        import scenario.text
    except ImportError:
        extendnamespacepackagepath(namespace_package=scenario, root_src_path=UTILS_SRC_PATH)
        import scenario.text
