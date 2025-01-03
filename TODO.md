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
    - Implement first .js and .css files:
        - Improve configuration page:
            - Size text areas.
    - Bug! Opera prevents Firefox from connecting to the server.
    - Display scenario results in campaign details page.
    - Display requirement texts with downstream traceability.
    - Upstream traceability:
        - Restore column order: req-verifiers on the left, req-ref on the right.
        - Display req comments.
        - Display step upstream traceability, folded by default.
    - Display scenario results (when applicable) in scenario pages.
    - Error "Erreur dans les liens source : request failed with status 404
      URL de la ressource : null
      URL du lien source : installHook.js.map"
      See https://firefox-source-docs.mozilla.org/devtools-user/debugger/source_map_errors/?utm_source=mozilla&utm_medium=firefox-console-errors&utm_campaign=default
    - Downstream traceability: Indent subrefs under related main requirements.
    - Use `.exec-result` popup for configuration page.
        - Possibly don't use POST? not sure.
    - Compare campaign result details?
    - Save campaign args in reports, in order to make it clear for partial campaign executions.
    - Add a 'req-mgt.py' tool that displays requirement test coverage.
        - Issue #xxx: Main logging indentation should be saved in scenario reports.
            - As displayed in logging.
            - Make main logging indentation not shift the logging level?
        - Display known issues.
        - Check campaign results display.
    - Implement JSON schemas.
    - Implement *expect-step-req-refinement* option.
        - Warning (known issue?) on test execution.
    - Add title and text with requirement subref.
    - Fix test regressions.
    - Implement tests:
        - Add req expectations. Check in scenario log & report.
        - Check full scenario log & report with requirements.
        - Complete scenario001 with SCENARIO_LOGGING testing.
        - Req management & subscenarios.
        - Req management & scenario reports.
        - Campaign reports: req-db, traceability reports.
        - Traceability reports: from suites and from campaign reports.
            - With or without test results.
        - Test scenario reports in YAML: single scenario & campaign executions (#74).
        - Check step requirement refinement.
    - Documentation:
        - Find out why we can't reference `scenario` symbols from `scenario.ui` with `..` in directives (like `:class:` at least).
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
- Issue #xxx: Remove `scenario` specific statistics in JUnit reports by default.
- Issue #xxx: Improve `Path`:
    - Memo: '//void/path' may lead to long network path resolutions...
    - Use a relative `pathlib.Path()` as `self._innerpath` for *void* paths.
    - Make `Path` methods fail for *void* paths.
- Issue #xxx: 'mkdoc.py' does not track undocumented class members.
- Issue #xxx: Don't use console colors directly, but use meta tags (like `<strong>` or `<span class=''>`).
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
    - And/or refactor steps as contexts => `with` statement would make it possible de define substeps under a main one, for:
        - Pre/post conditions,
        - Section / sub-test case,
        - No-verification actions => known issue filtering...
        - API to be defined.
        - Step indentation shall be refined meanwhile.
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


## Not planned

- Issue #65:
    - Extract _perfutils.py in a separate package.
    - Rework `_reflection.py` as a singleton.
        - Rework `FastPath.reflection_logger()` to `FastPath.reflection()` property.
        - Check that `getloadedmodulefrompath()` has actually been successfully optimized.
          It seems in the end we lost time with commit 30d8069 of 2024-09-06 on the 'bugfix/#65/optimize-scenario-instance-creation' branch.
    - Try to get rid of `FastPath.__slots__` and measure perf impacts.
