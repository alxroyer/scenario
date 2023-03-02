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

- Issue #72: Review `typing.TYPE_CHECKINGS` imports
- Issue #73: Use mypy v1.0.0
    - Avoid installing extra python libs in the global scope.
        - Interesting resource: https://stackoverflow.com/questions/1350466/preventing-python-code-from-importing-certain-modules#47854417
    - Check 'tools/conf/mypy.conf' v/s the up-to-date mypy.conf documentation.
    - Check issue065b => generate a known-issue only if the time lost is above 5%.
- Issue #70: CTRL+C does not stop a list of tests executed in a single command.
- Issue #63: Add the ability to give explanation texts.
    - Add a `explain()` method.
        - Use in knownissues110.
    - Use a type field with `StepSectionDescription`.
- Issue #69: Add stability tracking options
    - `--repeat` or `--loop` option: loops over a test execution, in order to evaluate a failure/succes ratio.
    - `--stop-fail` option: makes a campaign / test loop stop as soon as a test fails.
    - `--stop-success` option: makes a campaign / test loop stop as soon as a test succeeds.
- Issue #76: Don't install / uninstall python packages from tests.
    - Interesting resource: https://stackoverflow.com/questions/1350466/preventing-python-code-from-importing-certain-modules#47854417.
    - Remove related Internet sections in 'configdb320.py' and 'timezone001.py'.


## Roadmap to v0.3.0

- Issue #66: Avoid redefining `argparse` API.
    - Integrate branch 'feature/#66/use-argparse-directly'.
- Issue #58: Add sections for program arguments
    - Integrate branch 'feature/#66/use-argparse-directly'.


## Roadmap to v1.0.0

- Issue #32: Finalize scenario report JSON schema v1.
- Issue #13: Documentation:
    - Find better step objects / subscenario demos.
