> Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

- Issue #66: Avoid redefining `argparse` API.
    - Get rid of the `Args.addarg()` method and `ArgInfo` helper class.
    - Idea: Use reflexion for argument definitions (recognizing a '_arg...' or '_defarg...' method name pattern),
      and properties for typing and conversions.
- Issue #63: Add the ability to give explanation texts.
    - Add a `explain()` method.

LATER:
- Issue #67: Make typing infer a variable can't be `None` when `assertisnotnone()` has passed.
- Issue #60: Clarify typings for collections:
    - Use `typing.Sequence`, `typing.Collection` instead of `typing.List` or `typing.Iterable`.
    - Check deprecations since version 3.9 due to [PEP 585](https://peps.python.org/pep-0585/)
      and [Generic Alias Type](https://docs.python.org/3/library/stdtypes.html#types-genericalias).
        - Read from https://docs.python.org/3/library/typing.html#typing.Sequence.
        - Should we abandon Python 3.6 compliance?
- Issue #62: Refactor `EnsureInternetConnection`:
    1. `ping` options are not the same depending on the platform
    2. Prefer a `InternetSectionBegin` / `InternetSectionEnd` + goto approach (instead of `EnsureInternetConnection.isup()`).
- Issue #58: Add sections for program arguments
    - `--help` show be presented alone at first
    - Then default `scenario` options could be presented in a first dedicated section.
    - Then user defined launchers may set their own options in a dedicated section as well.
- Issue #39: Check `__str__()` and `__repr__()` implementations:
    - According to https://stackoverflow.com/questions/1436703/what-is-the-difference-between-str-and-repr#2626364
        - All classes shoud have a `__repr__()`.
        - And optionnally a `__str__()` when needed.
    - `__repr__()` is usually known as the "canonical string representation"
    - `__str__()` is usually known as the "printable string representation"
- Issue #54: Check when `TypeError` should be raised instead of `ValueError`.
- Issue #40:
    - Avoid mixing step objects and steps from method inspection.
    - Get rid of attribute definition with class members?
- Issue #23: Complete known issue handling.
    - Add known-issue severities.
    - *strict mode* / known-issue severity: Make known issues behave as errors as required.
    - Add a URL prefix.
- Issue #32: Fix scenario report JSON schema.
- Issue #41: Several test cases in a single script?
    - Could be a possibility to define several small test cases in a single file.
    - Question: how would they be named by the way?
    - Complete 'advanced.multiple-executions.rst'.
- Issue #8: Finalize tests:
    - Assertions
    - Evidence
    - Scenario attributes
    - Check whether scenario report href attribute is verified.
      Should be a relative path from the main path or the current working directory.
    - Config file
        - INI file with default section
        - With or without YAML installed
        - ...
    - Step sections:
        - Console output
        - JSON reports
        - skipped for statistics
        - ...
    - Scenario report JSON schema
    - Check input file encodings (test suite files, ...).
    - Campaign: check that saved log files are not colorized
      (reuse `logging510.CheckFileLogging`?).
- Issue #9: Add a `VERSION` constant
- Issue #13: Documentation: Fill in undocumented sections.
- Issue #14: Documentation: Track missing documentation for untyped attributes.
- Issue #15: Documentation: Set the final deliverable version: 1.0.0
- Issue #16: Publish under github.
    - Remove this 'TODO.md' file.
    - 'quickstart.rst': Check the repository URL.
    - Scenario reports: Check the JSON schema URL.
