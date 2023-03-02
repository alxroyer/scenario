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

import builtins
import importlib
import importlib.machinery
import importlib.util
import types
import typing

import scenario.test


# This list implements a cache that memorizes disabled package names.
_package_black_list = []  # type: typing.List[str]


def blacklistimporter(
        name,  # type: str
        globals=None,  # type: typing.Optional[typing.Mapping[str, typing.Any]]  # noqa  ## Shadows the built-in name 'globals'
        locals=None,  # type: typing.Optional[typing.Mapping[str, typing.Any]]  # noqa  ## Shadows the built-in name 'locals'
        fromlist=(),  # type: typing.Sequence[str]
        level=0,  # type: int
):  # type: (...) -> types.ModuleType
    """
    Inspired from https://stackoverflow.com/questions/1350466/preventing-python-code-from-importing-certain-modules#47854417.
    """
    if name in _package_black_list:
        raise ImportError(f"Module '{name}' black-listed")
    return importlib.__import__(name, globals, locals, fromlist, level)


# Install our `blacklistimporter()` function as the python global importer function.
# Inspired from https://stackoverflow.com/questions/1350466/preventing-python-code-from-importing-certain-modules#47854417.
builtins.__import__ = blacklistimporter


class PythonPackageBegin(scenario.StepSectionBegin):

    def __init__(
            self,
            pip_name,  # type: str
            import_name,  # type: str
            expected,  # type: bool
    ):  # type: (...) -> None
        scenario.StepSectionBegin.__init__(self)

        self.pip_name = pip_name  # type: str
        self.import_name = import_name  # type: str
        self.expected = expected  # type: bool

        self.is_installed = None  # type: typing.Optional[bool]

        # Override the base `StepSectionBegin.end` attribute with an instance of our `PythonPackageEnd` class.
        self.end = PythonPackageEnd(self)  # type: PythonPackageEnd

    def step(self):  # type: (...) -> None
        # Step description.
        super().step()

        if self.expected:
            self._stepexpected()
        else:
            self._stepunexpected()

    def _stepexpected(self):  # type: (...) -> None
        if self.ACTION(f"Check whether the '{self.import_name}' package can be imported."):
            # Check whether the package is installed.
            _module_spec = importlib.util.find_spec(self.import_name)  # type: typing.Optional[importlib.machinery.ModuleSpec]
            self.is_installed = (_module_spec is not None)
            self.evidence(f"Module spec for '{self.import_name}': {scenario.debug.saferepr(_module_spec)}")

            # Ensure the package is not in the black list.
            self.assertnotin(self.import_name, _package_black_list, f"Package '{self.import_name}' should not be black-listed")

        if self.ACTION(f"If the package is not available, skip next steps up to {self.end}."):
            if not self.is_installed:
                self.skipsection(
                    issue_level=scenario.test.IssueLevel.CONTEXT,
                    message=f"Package '{self.import_name}' not available",
                )

    def _stepunexpected(self):  # type: (...) -> None
        if self.ACTION(f"Ensure the '{self.import_name}' package can't be loaded."):
            # Set the disabled package name in the black list.
            _package_black_list.append(self.import_name)
            self.debug(f"Package black list: {_package_black_list!r}")

            # Make the package name being removed automatically from the black list in case of a failure before the end step.
            scenario.handlers.install(
                event=scenario.Event.AFTER_TEST,
                handler=self.end.cleanpackageblacklist,
                scenario=self.scenario,
                once=True,
            )


class PythonPackageEnd(scenario.StepSectionEnd):

    def __init__(
            self,
            begin,  # type: PythonPackageBegin
    ):  # type: (...) -> None
        scenario.StepSectionEnd.__init__(self, begin)

        # Override the base `StepSectionEnd.begin` attribute with an instance of our `PythonPackageBegin` class.
        self.begin = begin  # type: PythonPackageBegin

    def step(self):  # type: (...) -> None
        # Step description.
        super().step()

        if not self.begin.expected:
            if self.ACTION(f"Make the '{self.begin.import_name}' package loadable again."):
                # Call `cleanpackageblacklist()`.
                self.cleanpackageblacklist()

                # Ensure `cleanpackageblacklist()` won't be called again.
                scenario.handlers.uninstall(
                    event=scenario.Event.AFTER_TEST,
                    handler=self.cleanpackageblacklist,
                )

    def cleanpackageblacklist(
            self,
            *args  # type: typing.Any
    ):  # type: (...) -> None
        # Remove the package name from the black list.
        if self.begin.import_name in _package_black_list:
            _package_black_list.remove(self.begin.import_name)
            self.debug(f"Package black list: {_package_black_list!r}")
        else:
            self.warning(f"No such package '{self.begin.import_name}' in the black list")
