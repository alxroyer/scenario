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


#: Module paths which local imports should be avoided for.
OPTIMIZED_PATHS = [
    # _paths.SRC_PATH / "scenario",  # Not relevant.
    _paths.SRC_PATH / "scenario" / "_args.py",
    _paths.SRC_PATH / "scenario" / "_assertions.py",
    _paths.SRC_PATH / "scenario" / "_campaignargs.py",
    _paths.SRC_PATH / "scenario" / "_configdb.py",
    _paths.SRC_PATH / "scenario" / "_configkey.py",
    _paths.SRC_PATH / "scenario" / "_confignode.py",
    _paths.SRC_PATH / "scenario" / "_consoleutils.py",
    _paths.SRC_PATH / "scenario" / "_datetimeutils.py",
    _paths.SRC_PATH / "scenario" / "_debugclasses.py",
    _paths.SRC_PATH / "scenario" / "_debugutils.py",
    _paths.SRC_PATH / "scenario" / "_enumutils.py",
    _paths.SRC_PATH / "scenario" / "_issuelevels.py",
    _paths.SRC_PATH / "scenario" / "_knownissues.py",
    _paths.SRC_PATH / "scenario" / "_locations.py",
    _paths.SRC_PATH / "scenario" / "_logextradata.py",
    _paths.SRC_PATH / "scenario" / "_logfilters.py",
    _paths.SRC_PATH / "scenario" / "_logger.py",
    _paths.SRC_PATH / "scenario" / "_loggermain.py",
    _paths.SRC_PATH / "scenario" / "_loggingcontext.py",
    _paths.SRC_PATH / "scenario" / "_loghandler.py",
    _paths.SRC_PATH / "scenario" / "_path.py",
    _paths.SRC_PATH / "scenario" / "_reflection.py",
    _paths.SRC_PATH / "scenario" / "_req.py",
    _paths.SRC_PATH / "scenario" / "_reqdb.py",
    _paths.SRC_PATH / "scenario" / "_reqlink.py",
    _paths.SRC_PATH / "scenario" / "_reqref.py",
    _paths.SRC_PATH / "scenario" / "_reqverifier.py",
    _paths.SRC_PATH / "scenario" / "_scenarioargs.py",
    _paths.SRC_PATH / "scenario" / "_scenarioconfig.py",
    _paths.SRC_PATH / "scenario" / "_scenariodefinition.py",
    _paths.SRC_PATH / "scenario" / "_scenarioexecution.py",
    _paths.SRC_PATH / "scenario" / "_scenariologging.py",
    _paths.SRC_PATH / "scenario" / "_scenariorunner.py",
    _paths.SRC_PATH / "scenario" / "_scenariostack.py",
    _paths.SRC_PATH / "scenario" / "_setutils.py",
    _paths.SRC_PATH / "scenario" / "_stats.py",
    _paths.SRC_PATH / "scenario" / "_stepdefinition.py",
    _paths.SRC_PATH / "scenario" / "_stepexecution.py",
    _paths.SRC_PATH / "scenario" / "_stepsection.py",
    _paths.SRC_PATH / "scenario" / "_stepspecifications.py",
    _paths.SRC_PATH / "scenario" / "_textfileutils.py",
    _paths.SRC_PATH / "scenario" / "_textutils.py",
    _paths.SRC_PATH / "scenario" / "_timezoneutils.py",
]  # type: typing.Sequence[scenario.Path]
