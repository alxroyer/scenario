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

- Issue #21 (part): Avoid formatting debug strings when debug is disabled.
    - 2021-04-05: Done, but no significant optimization.
    - 2021-10-07: Retry giving logging arguments as positionals.
      O(15%) gain expected.
      Not sure that explains the main part of time taken.
- Issue #52: Opt for [f-strings (PEP 498)](https://www.python.org/dev/peps/pep-0498/)
  for non logging strings.
  O(10%) gain expected.
  Once again, not sure that explains the main part of the time taken.

- Issue #xxx: Check when `TypeError` should be raised instead of `ValueError`.
- Issue #xxx: 'configdb310.py' sometimes fail due to unexpected returns from a gateway:
    ```
    Executing $(ping -n 1 github.com)
      stdout:
      stdout: b"Envoi d'une requ\x88te 'ping' sur github.com [212.27.38.252] avec 32 octets de donn\x82es\xff:\r\n"
      stdout: b'R\x82ponse de 192.168.1.254\xff: Impossible de joindre le r\x82seau de destination.\r\n'
      stdout:
      stdout: Statistiques Ping pour 212.27.38.252:
      stdout: b'    Paquets\xff: envoy\x82s = 1, re\x87us = 1, perdus = 0 (perte 0%),\r\n'
    ```
    but the return code is 0 whatever the error displayed...
- Issue #xxx: Change `typing.List` to `typing.Sequence`
             and `typing.Dict` to `???` whenever possible.
- Issue #3: `Step.getactionresult()`: Actions/results shall be differenciated
  even though they are called several times (same location).
  This case may occur when tests are written with loops.
  Once fixed, rollback the additions of the p_description parameter additions
  in `ConsoleDisplay.stepdescription()` and `ConsoleDisplay.actionresult()`.
    - Check the interest of the `location` parameter in `ActionResultDefinition`'s
      constructor.
    - Check the docstring of the 'locations.py' module.
- Issue #21: Optimize.
    - Investigate on 'test/tests/jsonreport.py'
      (20 seconds before the test starts,
       at the time the test was a collection of ~10 test cases).
    - Rework the `LogStats` system in a general profiling system.
    - Avoid storing ACTION/RESULT locations?
      As far as I remember, this has been tried,
      without a visible gain.
    - Investigate on 'reflex.py' functions
      (`importmodulefrompath()` is less efficient
       when using `getloadedmodulefrompath()` for instance)
- Issue #23: Complete known issue handling.
    - *strict mode*: Make known issues behave as errors.
    - Add a URL prefix
- Issue #25: Avoid sphinx "duplicate object description" warnings.
    - Note: The documentation apparently seems to be generated as expected.
    - Misc:
        - Try to move 'doc/src/conf.py' in 'tools/conf/sphinx.py'
- Issue #38: Use `super()` when calling parent methods.
- Issue #39: Check `__str__()` and `__repr__()` implementations:
    - According to https://stackoverflow.com/questions/1436703/what-is-the-difference-between-str-and-repr#2626364
        - All classes shoud have a `__repr__()`.
        - And optionnally a `__str__()` when needed.
    - `__repr__()` is usually known as the "canonical string representation"
    - `__str__()` is usually known as the "printable string representation"
- Issue #32: Fix scenario report JSON schema.
- Issue #40:
    - Avoid mixing step objects and steps from method inspection.
    - Get rid of attribute definition with class members?
- Issue #41: Several test cases in a single script?
    - Could be a possibility to define several small test cases in a single file.
    - Question: how would they be named by the way?
    - Complete 'advanced.multiple-executions.rst'.
- Issue #22: Make the UTC timezone configurable.
    - Possibly restrict to UTC+0 only.
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
    - Issue #xxx: Documentation: Check all `:const:` rst directives => prefer ``
- Issue #14: Documentation: Track missing documentation for untyped attributes.
- Issue #15: Documentation: Set the final deliverable version: 1.0.0
- Issue #16: Publish under github.
    - Remove this 'TODO.md' file.
    - 'quickstart.rst': Check the repository URL.
    - Scenario reports: Check the JSON schema URL.
