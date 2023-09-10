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
    from ._errortrackerlogger import ErrorTrackerLogger as _ErrorTrackerLoggerImpl  # `ErrorTrackerLogger` used for inheritance.


class ModuleDeps(_ErrorTrackerLoggerImpl):

    class ComputationStatus(scenario.enum.StrEnum):
        NOT_STARTED = "not-started"
        COMPUTING = "computing"
        DONE = "done"

    all = {}  # type: typing.Dict[scenario.Path, ModuleDeps]

    @staticmethod
    def get(
            path,  # type: scenario.Path
    ):  # type: (...) -> ModuleDeps
        if path not in ModuleDeps.all:
            ModuleDeps.all[path] = ModuleDeps(path)
            ModuleDeps.all[path].debug("New module deps instance")
        return ModuleDeps.all[path]

    def __init__(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> None
        from ._moduleparser import ModuleParser

        _ErrorTrackerLoggerImpl.__init__(self, f"{path}:")

        self.parser = ModuleParser(path)  # type: ModuleParser
        self._deps = None  # type: typing.Optional[typing.Sequence[ModuleDeps]]
        self.status = ModuleDeps.ComputationStatus.NOT_STARTED  # type: ModuleDeps.ComputationStatus
        self.score = 0  # type: int

    @property
    def path(self):  # type: () -> scenario.Path
        return self.parser.path

    @property
    def basename(self):  # type: () -> str
        return self.path.name

    @property
    def deps(self):  # type: () -> typing.Sequence[ModuleDeps]
        from .._paths import SRC_PATH
        from ._import import Import

        if self._deps is None:
            _deps = {}  # type: typing.Dict[scenario.Path, ModuleDeps]
            for _import in self.parser.module_level_imports:  # type: Import
                if (
                    (not _import.context.isifblocktype())
                    and _import.imported_module_final_path
                    and _import.imported_module_final_path.is_relative_to(SRC_PATH)
                    and (_import.imported_module_final_path not in _deps)
                ):
                    _deps[_import.imported_module_final_path] = ModuleDeps.get(_import.imported_module_final_path)
            self._deps = list(_deps.values())
        return self._deps

    def getscore(self):  # type: (...) -> int
        if self.status == ModuleDeps.ComputationStatus.COMPUTING:
            raise ImportError(f"Cyclic module dependency detected on {self.path}")

        if self.status == ModuleDeps.ComputationStatus.DONE:
            return self.score

        self.debug("Computing score...")
        with scenario.logging.pushindentation():
            self.status = ModuleDeps.ComputationStatus.COMPUTING
            self.score = max([
                # Ensure one value at least.
                0,
                # Recursive call on module deps.
                *[_dep.getscore() for _dep in self.deps],
            ]) + 1
            self.status = ModuleDeps.ComputationStatus.DONE
        self.debug("Score=%d...", self.score)
        return self.score
