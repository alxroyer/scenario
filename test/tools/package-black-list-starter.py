# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Intermediate starter script that ensures package black list configurations
before a final launcher script is executed.

Such an intermediate starter script is required for setting up our test conditions
before the non-test `scenario` processing takes place.

'configdb320.py' example:

- The 'configdb320.py' test disables the 'pyyaml' package in order to check how things go on when loading a YAML configuration file.
- The general 'bin/run-test.py' launcher is used as a subprocess (which script we won't modify for test purpose).
- In the `scenario` implementation, configuration files are loaded before the test launcher loads a test script for execution.
- Therefore, without this starter script, we have no opportunity to setup our test conditions before a YAML configuration file is loaded.
"""

import logging
import sys

import scenario
import scenario.test


def _main():  # type: (...) -> None
    # Main variables.
    _this_script_path = scenario.Path(__file__)  # type: scenario.Path
    # Memo:
    #  Avoid using `scenario.Logger` in this starter script
    #  in order to avoid 'Avoid logging anything before arguments have been parsed' errors.
    # _logger = scenario.Logger(_this_script_path.name).enabledebug(True)  # type: scenario.Logger
    _logger = logging.getLogger()  # type: logging.Logger

    # First of all, remove the first argument (this script actually).
    _logger.debug("sys.argv = %r", sys.argv)
    if scenario.Path(sys.argv[0]) != _this_script_path:
        raise RuntimeError(f"Unexpected first argument {sys.argv[0]!r}, should be '{_this_script_path}'")
    _logger.debug("Removing first argument: %r", sys.argv[0])
    del sys.argv[0]
    _logger.debug("sys.argv = %r", sys.argv)

    # Find and save package black list configurations from the command line.
    _logger.debug("Searching for package black list arguments...")
    _i = 0  # type: int
    while _i + 2 < len(sys.argv):
        if (sys.argv[_i + 0] == "--config-value") and (sys.argv[_i + 1] == scenario.test.reflection.PACKAGE_BLACK_LIST_CONF_KEY):
            _logger.debug("Package black list arguments detected: %r", sys.argv[_i:_i + 3])

            # Feed the black list from the given comma-separated package names.
            for _package_name in sys.argv[_i + 2].split(","):  # type: str
                _logger.debug("=> %r", _package_name.strip())
                scenario.test.reflection.PACKAGE_BLACK_LIST.append(_package_name.strip())
            _logger.debug("Package black list: %r", scenario.test.reflection.PACKAGE_BLACK_LIST)

            # Remove the 3 arguments just processed.
            _logger.debug("Removing 3 arguments: %r", sys.argv[_i:_i + 3])
            del sys.argv[_i:_i + 3]
            _logger.debug("sys.argv = %r", sys.argv)
        else:
            _i += 1

    # Execute the actual script.
    # Inspired from https://stackoverflow.com/questions/64016426/how-to-run-multiple-python-scripts-using-single-python-py-script#64016505.
    # The first argument should be a launcher script.
    assert sys.argv, f"Invalid remaining arguments {sys.argv!r}"
    assert sys.argv[0].endswith(".py"), f"Invalid script {sys.argv[0]!r}"
    _script_path = scenario.Path(sys.argv[0])  # type: scenario.Path
    _logger.debug("_script_path = %r", _script_path)
    assert _script_path.is_file(), f"No such file {_script_path!r}"

    # Read the script content.
    _script_content = _script_path.read_bytes()  # type: bytes
    _logger.debug("_script_content = %s", scenario.debug.SafeRepr(_script_content))

    # Execute the script.
    _logger.debug("Executing script %r with arguments %r...", _script_path, sys.argv[1:])
    exec(
        _script_content,
        {
            # Fix the `__file__` constant with the path of the actual script, otherwise the path of this script would remain!
            "__file__": _script_path.abspath,
            # Ensure `__name__` is set to `"__main__"`.
            "__name__": "__main__",
        },
    )


if __name__ == "__main__":
    _main()
