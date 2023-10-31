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
    - Issue #74: Rename "JSON reports" into "scenario reports":
        - Check YAML writing with indentation.
        - Add an option to choose the default scenario report suffix.
        - Test scenario reports in YAML.
    - Improve the way to display an exception stacktrace.
    - Add a 'req-mgt.py' tool that displays requirement test coverage.
        - Check docstrings.
        - Add a `scenario.unit_tests` configuration, used in `ReqManagement` and `CampaignRunner`.
        - Make `ReqManagement` load campaign results.
        - Make `CampaignRunner` generate upstream and downstream traceability reports.
        - Make *req-db*, upstream and downstream traceability file names configurable.
        - Implement `ReqHttpServer`.
    - Implement JSON schemas.
    - Implement *expect-step-req-refinement* option.
        - Warning (known issue?) on test execution.
    - Fix test regressions.
    - Implement tests:
        - Add req expectations. Check in scenario log & report.
        - Complete scenario001 with SCENARIO_LOGGING testing.
        - Req management & subscenarios.
        - Req management & scenario reports.
        - Campaign reports: req-db, traceability reports.
        - Traceability reports: from suites and from campaign reports.
    - Documentation:
        - Add demo for requirement management.
        - Req management: command line & HTTP server.
        - Document logging indentation context.
    - Limitation when using step methods => use scenario stack.
    - Deliver:
        - Check docstrings.
        - Cherry-pick `ScenarioConfig` refactoring in the 'int/v0.2.2+' branch.
        - Cherry-pick 'check-types.py' improvements + integration note in PyCharm in the 'int/v0.2.2+' branch.
        - Cherry-pick "Avoid logging before program arguments have been parsed" in the 'int/v0.2.2+' branch.
        - Cherry-pick 'mkdoc.py' & `scenario.tools.sphinx` fixes in the 'int/v0.2.2+' branch.
        - Cherry-pick `checkfuncqualname()` fix in the 'int/v0.2.2+' branch.
- Issue #xxx: Don't use console colors directly, but use meta tags (like `<strong>` or `<span class=''>`).
- Issue #xxx: Main logging indentation should be saved in scenario reports.
    - As displayed in logging.
    - Make main logging indentation not shift the logging level?
- Issue #xxx: Improve assertion error messages with evidence introductory text.
    - When `evidence` is fed with a text, error messages from assertions shall be prefixed with `f"{evidence}: ".
- Issue #xxx: Strengthen JSON reading & writing:
    - Secnario reports, requirement databases.
    - Provide JSON schemas.
    - Use github links for JSON schema.
    - Store `$schema` fields.
    - Store `$version` fields.
    - Display warnings when reading a while with a higher version than the current `scenario` version.
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


## Roadmap to v1.0.0

- Issue #32: Finalize scenario report JSON schema v1.
- Issue #13: Documentation:
    - Find better step objects / subscenario demos.
