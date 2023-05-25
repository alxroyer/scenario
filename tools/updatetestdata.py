#!/usr/bin/env python
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

import pathlib
import sys

# Path management.
MAIN_PATH = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(MAIN_PATH / "src"))
sys.path.append(str(MAIN_PATH / "test" / "src"))
sys.path.append(str(MAIN_PATH / "tools" / "src"))

if True:
    import scenario
    import scenario.test
    import scenario.tools


class UpdateTestData:

    def run(self):  # type: (...) -> None

        # Command line arguments.
        scenario.Args.setinstance(scenario.Args(class_debugging=False))
        scenario.Args.getinstance().setdescription("Test data update.")
        if not scenario.Args.getinstance().parse(sys.argv[1:]):
            sys.exit(int(scenario.Args.getinstance().error_code))

        scenario.Path.setmainpath(scenario.tools.paths.MAIN_PATH)

        self._updateconfigdbscenario()
        self._updatefailingscenario()
        self._updategotoscenario()
        self._updateknownissuesscenario()
        self._updatesimplescenario()
        self._updatesuperscenario()
        self._updatesyntaxerrorscenario()

    def _updateconfigdbscenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatefile

        _test_data = TestData(scenario.test.paths.CONFIG_DB_SCENARIO, {
            "set": "ConfigDbScenario.step000",
        })  # type: TestData
        updatefile(
            scenario.tools.paths.TEST_CASES_PATH / "configdb" / "configdb020.py", _test_data,
            lambda file_updater, line: file_updater.matchmodifyline(
                rb'^(.* )\d+(,.* {2}# location: CONFIG_DB_SCENARIO/set)$', line,
                filter_match=None, location_key=lambda match: "set",
                new_line=lambda match, location: b'%s%d%s' % (match.group(1), location.line, match.group(2)),
            ),
        )

    def _updatefailingscenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatedataexpectations, updatejson

        _test_data = TestData(scenario.test.paths.FAILING_SCENARIO, {
            "step010": "FailingScenario.step010",
            "step010-exception": "FailingScenario.step010",
            "step020": "FailingScenario.step020",
        })  # type: TestData
        updatedataexpectations(_test_data)
        updatejson(scenario.test.paths.FAILING_SCENARIO.with_suffix(".doc-only.json"), _test_data, [
            # Steps:
            "step010", "step020",
        ])
        updatejson(scenario.test.paths.FAILING_SCENARIO.with_suffix(".executed.json"), _test_data, [
            "step010",
            "step010-exception",  # Step errors.
            "step010-exception",  # Action errors.
            "step020",
            "step010-exception",  # Scenario errors.
        ])

    def _updategotoscenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatejson

        _test_data = TestData(scenario.test.paths.GOTO_SCENARIO, {
            "step000": "GotoScenario.step000",
            "step010": "GotoScenario.step010",
            "step020": "GotoScenario.step020",
            "step030": "GotoScenario.step030",
            "step040": "GotoScenario.step040",
        })  # type: TestData
        updatejson(scenario.test.paths.GOTO_SCENARIO.with_suffix(".doc-only.json"), _test_data, [
            # Steps:
            "step000", "step010", "step020", "step030", "step040",
        ])
        updatejson(scenario.test.paths.GOTO_SCENARIO.with_suffix(".executed.json"), _test_data, [
            # Steps:
            "step000", "step010", "step020", "step030", "step040",
        ])

    def _updateknownissuesscenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatedataexpectations, updatejson

        _test_data = TestData(scenario.test.paths.KNOWN_ISSUES_SCENARIO, {
            "#---": "KnownIssuesScenario.__init__",
            "KnownIssuesStep": "KnownIssuesScenario.KnownIssuesStep",
            "#000": "KnownIssuesScenario.KnownIssuesStep.__init__",
            "#001": "KnownIssuesScenario.KnownIssuesStep.step",
            "#002": "KnownIssuesScenario.KnownIssuesStep.step",
            "Step-fail": "KnownIssuesScenario.KnownIssuesStep.step",
            "#003": "KnownIssuesScenario.KnownIssuesStep.step",
            "#004": "KnownIssuesScenario.KnownIssuesStep.step",
            "step010": "KnownIssuesScenario.step010",
            "#011": "KnownIssuesScenario.step010",
            "#012": "KnownIssuesScenario.step010",
            "step010-fail": "KnownIssuesScenario.step010",
            "#013": "KnownIssuesScenario.step010",
            "#014": "KnownIssuesScenario.step010",
            "step020": "KnownIssuesScenario.step020",
        })  # type: TestData
        updatedataexpectations(_test_data)
        updatejson(scenario.test.paths.KNOWN_ISSUES_SCENARIO.with_suffix(".doc-only.json"), _test_data, [
            # Steps:
            "KnownIssuesStep", "step010", "step020",
            # Scenario warnings:
            "#---",  # KnownIssuesScenario.__init__()
            "#000",  # KnownIssuesScenario.KnownIssuesStep.__init__()
            "#001", "#004",  # KnownIssuesScenario.KnownIssuesStep.step()
            "#011", "#014",  # KnownIssuesScenario.step010()
        ])
        updatejson(scenario.test.paths.KNOWN_ISSUES_SCENARIO.with_suffix(".executed.json"), _test_data, [
            # Steps:

            # - KnownIssuesScenario.KnownIssuesStep:
            "KnownIssuesStep",
            #     - Step warnings:
            "#000", "#001", "#002", "#003", "#004",
            #     - Action/result warnings:
            "#002", "#003",

            # - KnownIssuesScenario.step010():
            "step010",
            #     - Step warnings:
            "#011", "#012", "#013", "#014",
            #     - Action/result warnings:
            "#012", "#013",

            # - KnownIssuesScenario.step020():
            "step020",

            # Scenario warnings:
            # - KnownIssuesScenario:
            "#---",  # __init__()
            # - KnownIssuesScenario.KnownIssuesStep:
            "#000",  # __init__()
            "#001", "#002", "#003", "#004",  # step()
            # - KnownIssuesScenario.step010():
            "#011", "#012", "#013", "#014",
        ])

    def _updatesimplescenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatejson, updatelog

        _test_data = TestData(scenario.test.paths.SIMPLE_SCENARIO, {
            "step010": "SimpleScenario.step010",
            "step020": "SimpleScenario.step020",
            "step030": "SimpleScenario.step030",
        })  # type: TestData
        updatelog(scenario.test.paths.SIMPLE_SCENARIO.with_suffix(".doc-only.log"), _test_data, [
            # Steps:
            "step010", "step020", "step030",
        ])
        updatejson(scenario.test.paths.SIMPLE_SCENARIO.with_suffix(".doc-only.json"), _test_data, [
            # Steps:
            "step010", "step020", "step030",
        ])
        updatelog(scenario.test.paths.SIMPLE_SCENARIO.with_suffix(".executed.log"), _test_data, [
            # Steps:
            "step010", "step020", "step030",
        ])
        updatejson(scenario.test.paths.SIMPLE_SCENARIO.with_suffix(".executed.json"), _test_data, [
            # Steps:
            "step010", "step020", "step030",
        ])
        updatejson(scenario.test.paths.SUPERSCENARIO_SCENARIO.with_suffix(".executed.json"), _test_data, [
            # Steps:
            "step010", "step020", "step030",
        ])

    def _updatesuperscenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatejson

        _test_data = TestData(scenario.test.paths.SUPERSCENARIO_SCENARIO, {
            "step001": "SuperScenario.step001",
        })  # type: TestData
        updatejson(scenario.test.paths.SUPERSCENARIO_SCENARIO.with_suffix(".doc-only.json"), _test_data, [
            # Steps:
            "step001",
        ])
        updatejson(scenario.test.paths.SUPERSCENARIO_SCENARIO.with_suffix(".executed.json"), _test_data, [
            # Steps:
            "step001",
        ])

    def _updatesyntaxerrorscenario(self):  # type: (...) -> None
        from scenario.tools.updatetestdata import TestData, updatefile

        _test_data = TestData(scenario.test.paths.SYNTAX_ERROR_SCENARIO, {
            "syntax-error": "InvalidScenario.step010",
        })  # type: TestData
        updatefile(
            scenario.tools.paths.TEST_CASES_PATH / "issues" / "issue046.py", _test_data,
            lambda file_updater, line: file_updater.matchmodifyline(
                rb'^(.*, line )\d+(.* {2}# location: SYNTAX_ERROR_SCENARIO/syntax-error)$', line,
                filter_match=None, location_key=lambda match: "syntax-error",
                new_line=lambda match, location: b'%s%d%s' % (match.group(1), location.line, match.group(2)),
            ),
        )


if __name__ == "__main__":
    UpdateTestData().run()
