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


class ScenarioAttribute(scenario.enum.StrEnum):

    # Test title: Short description of the test.
    # As short as possible: usually couple of words only, in the nominal form.
    TEST_TITLE = "TEST_TITLE"

    # Test objective: More detailed sentence detailing the objective(s) of the test.
    TEST_OBJECTIVE = "TEST_OBJECTIVE"

    # Requirements: Features that the test covers.
    # Handled directly by the `scenario` framework.
    # FEATURES = "FEATURES"
