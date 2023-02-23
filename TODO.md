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

- Issue #72: Review `typing.TYPE_CHECKINGS` imports.
    - Check 'test/', 'tools/'.
    - Check what it gives in the documentation extracted with Sphinx.
        - Class renames are fixed to original names in the output documentation.
        - But `typing.TYPE_CHECKING` breaks the link to the actual class.
        - Seems that the issue is still opened in sphinx-autodoc: https://github.com/tox-dev/sphinx-autodoc-typehints/issues/22.
        - A plugin exists around typehints: https://pypi.org/project/sphinx-autodoc-typehints/
            - Perhaps a good option to fix typing issues, see options at https://pythonawesome.com/type-hints-support-for-the-sphinx-autodoc-extension/
            - Installation:
              ```
              $ pip install sphinx-autodoc-typehints
              Collecting sphinx-autodoc-typehints
                Downloading sphinx_autodoc_typehints-1.12.0-py3-none-any.whl (9.4 kB)
              Requirement already satisfied: Sphinx>=3.0 in c:\python36\lib\site-packages (from sphinx-autodoc-typehints) (4.4.0)
              Requirement already satisfied: packaging in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (21.3)
              Requirement already satisfied: sphinxcontrib-devhelp in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (1.0.2)
              Requirement already satisfied: imagesize in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (1.3.0)
              Requirement already satisfied: snowballstemmer>=1.1 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (2.2.0)
              Requirement already satisfied: sphinxcontrib-applehelp in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (1.0.2)
              Requirement already satisfied: Jinja2>=2.3 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (3.0.3)
              Requirement already satisfied: Pygments>=2.0 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (2.11.2)
              Requirement already satisfied: sphinxcontrib-htmlhelp>=2.0.0 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (2.0.0)
              Requirement already satisfied: babel>=1.3 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (2.9.1)
              Requirement already satisfied: docutils<0.18,>=0.14 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (0.17.1)
              Requirement already satisfied: requests>=2.5.0 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (2.27.1)
              Requirement already satisfied: alabaster<0.8,>=0.7 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (0.7.12)
              Requirement already satisfied: sphinxcontrib-serializinghtml>=1.1.5 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (1.1.5)
              Requirement already satisfied: sphinxcontrib-qthelp in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (1.0.3)
              Requirement already satisfied: importlib-metadata>=4.4 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (4.8.3)
              Requirement already satisfied: colorama>=0.3.5 in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (0.4.4)
              Requirement already satisfied: sphinxcontrib-jsmath in c:\python36\lib\site-packages (from Sphinx>=3.0->sphinx-autodoc-typehints) (1.0.1)
              Requirement already satisfied: pytz>=2015.7 in c:\python36\lib\site-packages (from babel>=1.3->Sphinx>=3.0->sphinx-autodoc-typehints) (2022.7.1)
              Requirement already satisfied: typing-extensions>=3.6.4 in c:\python36\lib\site-packages (from importlib-metadata>=4.4->Sphinx>=3.0->sphinx-autodoc-typehints) (4.1.1)
              Requirement already satisfied: zipp>=0.5 in c:\python36\lib\site-packages (from importlib-metadata>=4.4->Sphinx>=3.0->sphinx-autodoc-typehints) (3.6.0)
              Requirement already satisfied: MarkupSafe>=2.0 in c:\python36\lib\site-packages (from Jinja2>=2.3->Sphinx>=3.0->sphinx-autodoc-typehints) (2.0.1)
              Requirement already satisfied: urllib3<1.27,>=1.21.1 in c:\python36\lib\site-packages (from requests>=2.5.0->Sphinx>=3.0->sphinx-autodoc-typehints) (1.26.8)
              Requirement already satisfied: charset-normalizer~=2.0.0 in c:\python36\lib\site-packages (from requests>=2.5.0->Sphinx>=3.0->sphinx-autodoc-typehints) (2.0.10)
              Requirement already satisfied: certifi>=2017.4.17 in c:\python36\lib\site-packages (from requests>=2.5.0->Sphinx>=3.0->sphinx-autodoc-typehints) (2021.10.8)
              Requirement already satisfied: idna<4,>=2.5 in c:\python36\lib\site-packages (from requests>=2.5.0->Sphinx>=3.0->sphinx-autodoc-typehints) (3.3)
              Requirement already satisfied: pyparsing!=3.0.5,>=2.0.2 in c:\python36\lib\site-packages (from packaging->Sphinx>=3.0->sphinx-autodoc-typehints) (3.0.7)
              Installing collected packages: sphinx-autodoc-typehints
              Successfully installed sphinx-autodoc-typehints-1.12.0
              ```
            - Using this plugin leads to tens of errors like:
              "Cannot resolve forward reference in type annotations of "scenario.actionresultexecution.ActionResultExecution": name '_ActionResultDefinitionType' is not defined"
            - But [version 1.12.0](https://github.com/tox-dev/sphinx-autodoc-typehints/releases/tag/1.12.0) dates from 2021-04-15,
              while the latest [version 1.22.0](https://github.com/tox-dev/sphinx-autodoc-typehints/releases/tag/1.22.0) dates from 2023-01-31.
            - Indeed [version 1.12.0](https://pypi.org/project/sphinx-autodoc-typehints/1.12.0/) is latest compatible with Python >=3.6,
              [version 1.13.0](https://pypi.org/project/sphinx-autodoc-typehints/1.13.0/) dating from 2022-01-01 is compatible with Python >=3.7,
              and [version 1.22](https://pypi.org/project/sphinx-autodoc-typehints/1.22/) still compatible with Python >=3.7.
            - Using the `set_type_checking_flag` option presented by https://pythonawesome.com/type-hints-support-for-the-sphinx-autodoc-extension/
              does not seem to change anything.
            - Note: The `set_type_checking_flag` option stated by https://pythonawesome.com/type-hints-support-for-the-sphinx-autodoc-extension/
              seems not existing anymore in the [up-to-date versions](https://github.com/tox-dev/sphinx-autodoc-typehints/blob/1.22.0/src/sphinx_autodoc_typehints/__init__.py#L801):
                - Page dating from 2021-11-23.
                - Option actually existed in [version 1.13.1](https://github.com/tox-dev/sphinx-autodoc-typehints/blob/1.13.1/src/sphinx_autodoc_typehints/__init__.py#L502).
                - Also existed in [version 1.12.0](https://github.com/tox-dev/sphinx-autodoc-typehints/blob/1.12.0/sphinx_autodoc_typehints.py#L483)
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
- Issue #73: Use mypy v1.0.0.
    - Requires Python >= 3.7.
    - Try to revert mypy@0.971 workarounds in 'src/scenario/path.py'.
    - Update `coding-rules.py.compat` section.
