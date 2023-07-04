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

if True:
    from simplescenario import SimpleScenario as _SimpleScenarioImpl  # `SimpleScenario` used for inheritance.


class InheritingScenario(_SimpleScenarioImpl):

    def __init__(self):  # type: (...) -> None
        _SimpleScenarioImpl.__init__(
            self,
            title="Inheriting scenario sample",
        )

    def step015(self):  # type: (...) -> None
        self.STEP("InheritingScenario.step#15")

        self.ACTION("Pellentesque diam volutpat commodo sed egestas egestas.")
        self.RESULT("Massa tincidunt dui ut ornare.")
