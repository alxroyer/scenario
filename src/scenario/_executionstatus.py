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
Execution status management.
"""

from ._enumutils import StrEnum  # `StrEnum` used for inheritance.


class ExecutionStatus(StrEnum):
    """
    Scenario & campaign execution status.
    """
    #: Success.
    SUCCESS = "SUCCESS"
    #: Success with warnings.
    WARNINGS = "WARNINGS"
    #: Failure.
    FAIL = "FAIL"
    #: Test skipped.
    SKIPPED = "SKIPPED"
    #: Unknown status.
    UNKOWN = "UNKNOWN"
