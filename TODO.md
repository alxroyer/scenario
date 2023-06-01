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

- Issue #77: Clarify project imports.
    - Check what happens for `if typing.TYPE_CHECKING:` import in 'scenario/test/_expectations/__init__.py'.
    - Check documentation.
        - Add references to imports in `coding-rules.py.namings` regarding leading underscores for imported classes and types.
        - Add reference to imports in `coding-rules.py.namings` regarding "Type" suffixes for types and imported classes.
        - Add 'checkmoduleimports.py' in the guidelines.
        - All module imports prefixed with '_': those required for execution, as well as types defined in neighbour modules.
        - Project imports required for execution:
            - Indented in `if True:` blocks: in order to avoid editors folding implementation imports with the system imports.
            - Or in `try:` blocks for reexports: otherwise we may get "unused" warnings.
            - One line per import.
            - Suffixed with 'Impl' (except for modules).
        - Reexports in `try: ... except: pass`, not `itTrue:` otherwise the symbols are noted are unused.
        - Update module naming coding rules: use hyphens in executable scripts.
- Move `getstepexecution()` from '_assertionhelpers.py' to `StepExecution`.
- Issue #79: Hazardous behaviour of `ScenarioDefinition.getstep()`.
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

- Issue #66: Avoid redefining `argparse` API.
    - Integrate branch 'feature/#66/use-argparse-directly'.
- Issue #58: Add sections for program arguments.
    - Integrate branch 'feature/#66/use-argparse-directly'.
- Issue #74: Rename JSON reports into something else.


## Roadmap to v1.0.0

- Issue #32: Finalize scenario report JSON schema v1.
- Issue #13: Documentation:
    - Find better step objects / subscenario demos.
