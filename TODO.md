> Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
>
> Licensed under the Apache License, Version 2.0 (the "License");
> you may not use this file except in compliance with the License.
> You may obtain a copy of the License at
>
>     http://www.apache.org/licenses/LICENSE-2.0
>
> Unless required by applicable law or agreed to in writing, software
> distributed under the License is distributed on an "AS IS" BASIS,
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
> See the License for the specific language governing permissions and
> limitations under the License.


# TODO

## Roadmap to v0.2.3

- Issue #83: Add the ability to track requirements.
    - Choose between "sub-class" and "subclass" spellings >> "subclass" (according to Wiktionary).
    - Get rid of `OrderedSetHelper`, use global functions packaged in an '_orderedset.py' module instead.
    - Save requirement database with campaign reports.
    - Cherry-pick `ScenarioConfig` refactoring in the 'int/v0.2.2+' branch.
    - Cherry-pick 'check-types.py' improvements + integration note in PyCharm in the 'int/v0.2.2+' branch.
    - Cherry-pick "Avoid logging before program arguments have been parsed" in the 'int/v0.2.2+' branch.
    - Cherry-pick 'mkdoc.py' & `scenario.tools.sphinx` fixes in the 'int/v0.2.2+' branch.
    - Cherry-pick `checkfuncqualname()` fix in the 'int/v0.2.2+' branch.
    - Make `ReqDatabase.reqid2xxx()` handle requirement subkeys.
    - Simplify `self.DESC()`, `self.ACTION()`, `self.RESULT()`, `scenario.REQ()` calls.
    - Add a 'check-test-coverage.py' tool that displays requirement test coverage.
        - Shall work either on test suite files, or campaign results.
    - Add the ability to make the test check that its scenario links are detailed by step links.
    - Complete scenario001 with SCENARIO_LOGGING testing.
    - Fix test regressions:
        - Campaigns:
            - campaign001.py
            - campaign002.py
            - campaign003.py
            - campaign004.py
            - campaign005.py
        - "1 != <ErrorCode.ENVIRONMENT_ERROR: 40>":
            - configdb320.py
        - "JSON {} | 'tests.total' => Missing item":
            - issue042.py
            - knownissues080.py
            - knownissues180.py
            - knownissues190.py
            - knownissues380.py
            - knownissues480.py
            - multiplescenarios000.py
            - multiplescenarios001.py
            - multiplescenarios002.py
            - multiplescenarios003.py
            - multiplescenarios004.py
        - "KeyError: 'time'":
            - issue065b.py
        - "len(['      ERROR    FAIL', '      ERROR    FAIL']) is not...":
            - knownissues090.py
            - knownissues390.py
            - knownissues490.py
        - "b'  DESCRIPTION:' != b''":
            - scenariologging010.py
            - scenariologging011.py
    - Implement tests:
        - Campaign reports.
        - Scenario reports.
        - 'check-test-coverage.py'.
    - Add documentation with demo.
    - Document logging indentation context.
    - Limitation when using step methods => use scenario stack.
    - Implement *check_step_coverage* option.
    - `covers()` and `coveredby()` in execution mode should do nothing.
    - Check docstrings.
    - Add a HTTP server that displays pages on requirement management.
- Issue #80: Provide a subscenario step class.
    - Enable `ScenarioDefinition.getstep()` to walk through subscenarios when looking for a given step by the way.
- Issue #70: CTRL+C does not stop a list of tests executed in a single command.
- Issue #63: Add the ability to give explanation texts.
    - Add a `explain()` method.
        - Use in knownissues110.
    - Use a type field with `StepSectionDescription`.
- Issue #69: Add stability tracking options
    - `--repeat` or `--loop` option: loops over a test execution, in order to evaluate a failure/succes ratio.
    - `--stop-fail` option: makes a campaign / test loop stop as soon as a test fails.
    - `--stop-success` option: makes a campaign / test loop stop as soon as a test succeeds.
- Issue #78: Contribute to sphinx-autodoc-typehints#22, replying to https://github.com/tox-dev/sphinx-autodoc-typehints/issues/22#issuecomment-423289499


## Roadmap to v0.3.0

- Issue #84: Enforce named parameters when appropriate.
    - Known issues,
    - ...
- Issue #66: Avoid redefining `argparse` API.
    - Integrate branch 'feature/#66/use-argparse-directly'.
- Issue #58: Add sections for program arguments.
    - Integrate branch 'feature/#66/use-argparse-directly'.
- Issue #74: Rename JSON reports into something else.


## Roadmap to v1.0.0

- Issue #32: Finalize scenario report JSON schema v1.
- Issue #13: Documentation:
    - Find better step objects / subscenario demos.
