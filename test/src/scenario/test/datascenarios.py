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

import sys

from . import paths

# Path management.
sys.path.append(str(paths.DATA_PATH))


try:
    from actionresultloopscenario import ActionResultLoopScenario as ActionResultLoopScenario
    from configdbscenario import ConfigDbScenario as ConfigDbScenario
    from failingscenario import FailingScenario as FailingScenario
    from gotoscenario import GotoScenario as GotoScenario
    from inheritingscenario import InheritingScenario as InheritingScenario
    from knownissuedetailsscenario import KnownIssueDetailsScenario as KnownIssueDetailsScenario
    from knownissuesscenario import KnownIssuesScenario as KnownIssuesScenario
    from loggerscenario import LoggerScenario as LoggerScenario
    from loggingindentationscenario import LoggingIndentationScenario as LoggingIndentationScenario
    from scenariologgingscenario import ScenarioLoggingScenario as ScenarioLoggingScenario
    from simplescenario import SimpleScenario as SimpleScenario
    from superscenario import SuperScenario as SuperScenario
    from waitingscenario import WaitingScenario as WaitingScenario
finally:
    pass