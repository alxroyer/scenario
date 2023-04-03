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

- Issue #77: Avoid exporting implementation modules.
    - Check 'reflex' terminology, 'reflective programming' or 'reflection' seem to be the right terms.
    - Fix documentation generation:
        - Can we use `:data:` or `:const:` directives, or even `:obj:`, for cross-referencing module attributes?
        - Choose between `#:` or docstrings placed after attributes and types.
        - Avoid expanding types in output documentation.
        - Check whether there are still missing references if we don't generate documentation for private modules.
        - Remove `scenario.logging` timestamps from `sphinxapidoc()` logs.
        - Change from `#:` Sphinx comments to `"""` doctrings?
        - Check whether `sphinx.ext.autodoc.object_description` hack can be removed.
    - Ensure "# The following `try` block avoids IDEs folding the following import lines." comments in '__init__.py' files when appropriate.
      Check whether an exception is caught and re-thrown, not just `pass`.
    - Search for "`.[^_]" patterns.
    - Search for "from \. import [^_]"
    - Update coding rules.
        - Module names.
        - Package definition and export strategy:
            - Private implementation: '_' prefix.
            - Comment may be set in docstring when public submodules shall be explicitly imported.
            - Avoid `from . import` pattern, but:
              ```python
              import full.path.to._privatepackagename as _privatepackagename
              publicpackagename = _privatepackagename
              ```
              Note: Seems can't be reexported (unfortunately).
            - BUT, it seems this pattern does not work with namespace packages with Python 3.6.
              For instance:
              ```python
              import scenario.tools._paths as _paths
              ```
              in 'tools/scenario/tools/__init__.py' fails with the following error:
              "AttributeError: module 'scenario' has no attribute 'tools'"
        - Save note on renamed class exports.
    - Use docstrings after module attribute instead of `.. py:atribute:` directives.
- Move `getstepexecution()` from '_assertionhelpers.py' to `StepExecution`.
- Issue #79: Hazardous behaviour of `ScenarioDefinition.getstep()`.
- Issue #80: Provide a subscenario step class.
    - Enable `ScenarioDefinition.getstep()` to walk through subscenarios when looking for a given step by the way.
- Clarify usage for `# noqa`.
    - See https://www.alpharithms.com/noqa-python-501210/.
    - Codes seem to be checker specific (`flake8` among others).
    - Don't use codes, prefer an explanatory comment after a double `##`.
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
