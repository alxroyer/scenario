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

if typing.TYPE_CHECKING:
    import scenario
import scenario.test


class JsonReportFileVerificationStep(scenario.test.VerificationStep):
    """
    Provides easy access to the JSON report path info.
    """

    @property
    def report_path(self):  # type: () -> scenario.Path
        assert self.subprocess.report_path, f"JSON report should have generated with {self.subprocess}"
        return self.subprocess.report_path
