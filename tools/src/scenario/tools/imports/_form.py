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

import typing

import scenario

if True:
    from .. import _paths as _paths  # @module-level-instantiation


class ImportForm(scenario.enum.StrEnum):
    SYSTEM_IMPORT = "import <package>"
    FROM_MODULE_IMPORT = "from <module> import <symbol>"
    IMPORT_MODULE_AS = "from <package> import <module>"


#: Specify non-:attr:`ImportForm.FROM_MODULE_IMPORT` imports only.
_IMPORT_FORMS = {
    _paths.SRC_PATH / "scenario" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.SRC_PATH / "scenario" / "_assertionhelpers.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_consoleutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_datetimeutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_debugutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_enumutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_jsondictutils.py": ImportForm.FROM_MODULE_IMPORT,  # Keep importing `JsonDictUtilsType` from '_jsondictutils.py'.
    _paths.SRC_PATH / "scenario" / "_perfutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_setutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_textfileutils.py": ImportForm.FROM_MODULE_IMPORT,  # Single `TextFile` class in '_textfileutils.py'.
    _paths.SRC_PATH / "scenario" / "_textutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_timezoneutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_typeutils.py": ImportForm.IMPORT_MODULE_AS,
    _paths.SRC_PATH / "scenario" / "_xmlutils.py": ImportForm.FROM_MODULE_IMPORT,  # Single `Xml` class in '_xmlutils.py'.
    _paths.SRC_PATH / "scenario" / "ui" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.TEST_SRC_PATH / "scenario" / "test" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.TEST_SRC_PATH / "scenario" / "test" / "_datascenarios.py": ImportForm.IMPORT_MODULE_AS,
    _paths.TEST_SRC_PATH / "scenario" / "test" / "_paths.py": ImportForm.IMPORT_MODULE_AS,
    _paths.TOOLS_SRC_PATH / "scenario" / "tools" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.TOOLS_SRC_PATH / "scenario" / "tools" / "imports" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.TOOLS_SRC_PATH / "scenario" / "tools" / "sphinx" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.TOOLS_SRC_PATH / "scenario" / "tools" / "_paths.py": ImportForm.IMPORT_MODULE_AS,
    _paths.UTILS_SRC_PATH / "scenario" / "inners" / "__init__.py": ImportForm.SYSTEM_IMPORT,
    _paths.UTILS_SRC_PATH / "scenario" / "text" / "__init__.py": ImportForm.SYSTEM_IMPORT,
}  # type: typing.Dict[scenario.Path, ImportForm]


def expectedform(
        path,  # type: scenario.Path
):  # type: (...) -> ImportForm
    # If defined in `_IMPORT_FORMS`.
    if path in _IMPORT_FORMS:
        return _IMPORT_FORMS[path]
    # Default to `FROM_MODULE_IMPORT`.
    return ImportForm.FROM_MODULE_IMPORT
