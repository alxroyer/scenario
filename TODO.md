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

## Roadmap to v0.3.0

- Improve README.md:
    - Publish documentation on readthedocs (check final settings).
    - Move 'doc/src/uml/uml.conf' in 'tools/conf/sphinx/'.
- Issue #66: Avoid redefining `argparse` API.
    - Get rid of the `Args.addarg()` method and `ArgInfo` helper class.
    - Idea: Use reflexion for argument definitions (recognizing a '_arg...' or '_defarg...' method name pattern),
      and properties for typing and conversions.
    - Check 'advanced.launcher.rst'.
- Issue #58: Add sections for program arguments
    - `--help` show be presented alone at first
    - Then default `scenario` options could be presented in a first dedicated section.
    - Then user defined launchers may set their own options in a dedicated section as well.
- Issue #70: CTRL+C does not stop a list of tests executed in a single command.
- Issue #63: Add the ability to give explanation texts.
    - Add a `explain()` method.
        - Use in knownissues110.
- Issue #69: Add stability tracking options
    - `--repeat` or `--loop` option: loops over a test execution, in order to evaluate a failure/succes ratio.
    - `--stop-fail` option: makes a campaign / test loop stop as soon as a test fails.
    - `--stop-success` option: makes a campaign / test loop stop as soon as a test succeeds.
- Issue #62: Refactor `EnsureInternetConnection`:
    1. `ping` options are not the same depending on the platform
    2. Prefer a `InternetSectionBegin` / `InternetSectionEnd` + goto approach (instead of `EnsureInternetConnection.isup()`).


## Roadmap to v1.0.0

- Issue #32: Fix scenario report JSON schema.
- Documentation:
    - Find better step objects / subscenario demos.
- Issue #15: Documentation: Set the final deliverable version: 1.0.0.
