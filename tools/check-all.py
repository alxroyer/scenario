#!/usr/bin/env python
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

import abc
import os
import pathlib
import re
import subprocess
import sys
import time
import typing

# Path management.
_root_scenario_path = pathlib.Path(__file__).parents[1].resolve()  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "tools" / "src"))

if True:
    import scenario  # @after-path-management
    import scenario.tools  # @after-path-management


class CheckAllArgs(scenario.Args):
    def __init__(self):  # type: (...) -> None
        scenario.Args.__init__(self, class_debugging=False)

        self.setdescription("All checker.")

        self._full = None  # type: typing.Optional[bool]
        self.addarg("Full", "_full", bool).define(
            "--full",
            action="store_true", default=None,
            help="Launch very all verifications, longer.",
        )
        self.addarg("Fast", "_full", bool).define(
            "--fast",
            action="store_false", default=None,
            help="Launch a subset of all verifications, to keep it fast.",
        )

        self.skip_check_files = False
        self.addarg(f"Skip {CheckAll.CHECK_FILES_TITLE!r}", "skip_check_files", bool).define(
            "--skip-check-files",
            action="store_true", default=False,
            help=f"Skip {CheckAll.CHECK_FILES_TITLE!r} verification.",
        )

        self.skip_check_license_headers = False
        self.addarg(f"Skip {CheckAll.CHECK_LICENSE_HEADERS_TITLE!r}", "skip_check_license_headers", bool).define(
            "--skip-check-license-headers",
            action="store_true", default=False,
            help=f"Skip {CheckAll.CHECK_LICENSE_HEADERS_TITLE!r} verification.",
        )

        self.skip_check_types = False
        self.addarg(f"Skip {CheckAll.CHECK_TYPES_TITLE!r}", "skip_check_types", bool).define(
            "--skip-check-types",
            action="store_true", default=False,
            help=f"Skip {CheckAll.CHECK_TYPES_TITLE!r} verification.",
        )

        self.skip_check_imports = False
        self.addarg(f"Skip {CheckAll.CHECK_IMPORTS_TITLE!r}", "skip_check_imports", bool).define(
            "--skip-check-imports",
            action="store_true", default=False,
            help=f"Skip {CheckAll.CHECK_IMPORTS_TITLE!r} verification.",
        )

        self.skip_check_schemas = False
        self.addarg(f"Skip {CheckAll.CHECK_SCHEMAS_TITLE!r}", "skip_check_schemas", bool).define(
            "--skip-check-schemas",
            action="store_true", default=False,
            help=f"Skip {CheckAll.CHECK_SCHEMAS_TITLE!r} verification.",
        )

        self.skip_req_mgt = False
        self.addarg(f"Skip {CheckAll.REQ_MGT_TITLE!r}", "skip_req_mgt", bool).define(
            "--skip-req-mgt",
            action="store_true", default=False,
            help=f"Skip {CheckAll.REQ_MGT_TITLE!r} verification.",
        )

        self.skip_campaign = False
        self.addarg(f"Skip {CheckAll.CAMPAIGN_TITLE!r}", "skip_campaign", bool).define(
            "--skip-campaign",
            action="store_true", default=False,
            help=f"Skip {CheckAll.CAMPAIGN_TITLE!r} verification.",
        )

        self.skip_mkdoc = False
        self.addarg(f"Skip {CheckAll.MKDOC_TITLE!r}", "skip_mkdoc", bool).define(
            "--skip-mkdoc",
            action="store_true", default=False,
            help=f"Skip {CheckAll.MKDOC_TITLE!r} verification.",
        )

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        if not super()._checkargs(args):
            return False

        if self._full is None:
            self.error("Please specify either --full or --fast")
            return False

        return True

    @property
    def full(self):  # type: () -> bool
        return bool(self._full)


class Console(abc.ABC):
    @staticmethod
    def print(
            msg,  # type: str
    ):  # type: (...) -> None
        """
        Ensures printing in stdout without interleaving with subprocess outputs.
        """
        print(msg)
        sys.stdout.flush()


class Command:
    @staticmethod
    def title(
            title,  # type: str
    ):  # type: (...) -> None
        Console.print("")
        Console.print(f"=== {title} ===")

    @staticmethod
    def execute(
            command,  # type: typing.Sequence[str]
            *,
            show_exec_time=True,  # type: bool
            expect_error="",  # type: str
    ):  # type: (...) -> None
        Command(
            command=command,
            show_exec_time=show_exec_time,
            expect_error=expect_error,
        )._execute()

    def __init__(
            self,
            *,
            command,  # type: typing.Sequence[str]
            show_exec_time,  # type: bool
            expect_error,  # type: str
    ):  # type: (...) -> None
        self.command = command  # type: typing.Sequence[str]
        self.show_exec_time = show_exec_time  # type: bool
        self.expect_error = expect_error  # type: str

    def commanddesc(
            self,
            hide_interpreter,  # type: bool
    ):  # type: (...) -> str
        """
        Command description computation.

        Ensures POSIX paths.

        :param hide_interpreter: ``True`` to completely hide the intepreter. ``False`` to keep it, but make it short (basename without suffix).
        :return: Command description string.
        """
        _command = list(self.command)  # type: typing.List[str]

        # Process interpreter.
        if (len(_command) > 1) and (_command[0] == sys.executable):
            if hide_interpreter:
                del _command[0]
            else:
                _command[0] = pathlib.Path(sys.executable).stem

        # Ensure POSIX paths.
        for _index, _arg in enumerate(_command):  # type: int, str
            if pathlib.Path(_arg).exists():
                _command[_index] = pathlib.Path(_arg).as_posix()
            elif (not pathlib.Path(_arg).is_absolute()) and (scenario.tools.paths.ROOT_SCENARIO_PATH / _arg).exists():
                _command[_index] = pathlib.Path(_arg).as_posix()

        return " ".join(_command)

    def _execute(self):  # type: (...) -> None
        _prompt = f"{scenario.tools.paths.ROOT_SCENARIO_PATH.abspath}>"  # type: str
        _command_desc = self.commanddesc(hide_interpreter=False)  # type: str

        Console.print(f"{_prompt} {_command_desc}")
        try:
            _t0 = time.time()  # type: float
            _res = subprocess.run(self.command, cwd=scenario.tools.paths.ROOT_SCENARIO_PATH)  # type: subprocess.CompletedProcess[bytes]
            if self.show_exec_time:
                Console.print(f"(Execution time: {scenario.datetime.f2strduration(time.time() - _t0)})")

            if not self.expect_error:
                if _res.returncode != 0:
                    Console.print(f"{_prompt} {_command_desc} (error code: {_res.returncode})")
                    sys.exit(1)
            else:
                if _res.returncode == 0:
                    Console.print(f"{_prompt} {_command_desc} ({self.expect_error})")
                    sys.exit(1)
        except KeyboardInterrupt:
            Console.print(f"{_prompt} {_command_desc} (interrupted)")
            sys.exit(1)


class CheckAll(abc.ABC):
    @staticmethod
    def execute():  # type: (...) -> None
        _t0 = time.time()  # type: float
        try:
            if CheckAllArgs.getinstance().full:
                # Call `_checkfiles()` in strict mode at the very end.
                # CheckAll._checkfiles()
                CheckAll._checklicenseheaders()
            else:
                CheckAll._checkfiles()
            CheckAll._checktypes()
            CheckAll._checkimports()
            CheckAll._checkschemas()
            CheckAll._reqmgt()
            if CheckAllArgs.getinstance().full:
                CheckAll._campaign()
            CheckAll._mkdoc()
            if CheckAllArgs.getinstance().full:
                CheckAll._checkfiles()
        finally:
            Console.print("")
            Console.print(f"Total execution time: {scenario.datetime.f2strduration(time.time() - _t0)}")

    CHECK_FILES_TITLE = "Check files"  # type: str

    @classmethod
    def _checkfiles(cls):  # type: (...) -> None
        Command.title(cls.CHECK_FILES_TITLE)
        if CheckAllArgs.getinstance().skip_check_files:
            scenario.logging.warning("Skipped")
        else:
            # Search for 'repo-checkfiles' from the `PATH` environment variable.
            for _env_path in (os.environ.get("PATH") or "").split(os.pathsep):  # type: str
                _repo_checkfiles_path = pathlib.Path(_env_path) / "repo-checkfiles"  # type: pathlib.Path
                if _repo_checkfiles_path.is_file():
                    # If found, execute the command.
                    if CheckAllArgs.getinstance().full:
                        Command.execute([sys.executable, str(_repo_checkfiles_path), "--all", "--strict"])
                    else:
                        Command.execute([sys.executable, str(_repo_checkfiles_path)])
                    break
            else:
                scenario.logging.warning("'repo-checkfiles' script can't be found from PATH")

    CHECK_LICENSE_HEADERS_TITLE = "Check license headers"  # type: str

    @classmethod
    def _checklicenseheaders(cls):  # type: (...) -> None
        Command.title(cls.CHECK_LICENSE_HEADERS_TITLE)
        if CheckAllArgs.getinstance().skip_check_license_headers:
            scenario.logging.warning("Skipped")
        else:
            # Search for 'repo-checklicenseheaders' from the `PATH` environment variable.
            for _env_path in (os.environ.get("PATH") or "").split(os.pathsep):  # type: str
                _repo_checklicenseheaders_path = pathlib.Path(_env_path) / "repo-checklicenseheaders"  # type: pathlib.Path
                if _repo_checklicenseheaders_path.is_file():
                    # If found, execute the command.
                    if CheckAllArgs.getinstance().full:
                        Command.execute([sys.executable, str(_repo_checklicenseheaders_path), "--strict"])
                    else:
                        Command.execute([sys.executable, str(_repo_checklicenseheaders_path)])
                    break
            else:
                scenario.logging.warning("'repo-checklicenseheaders' script can't be found from PATH")

    CHECK_TYPES_TITLE = "Check types"  # type: str

    @classmethod
    def _checktypes(cls):  # type: (...) -> None
        Command.title(cls.CHECK_TYPES_TITLE)
        if CheckAllArgs.getinstance().skip_check_types:
            scenario.logging.warning("Skipped")
        else:
            Command.execute([sys.executable, "tools/check-types.py"])

    CHECK_IMPORTS_TITLE = "Check imports"  # type: str

    @classmethod
    def _checkimports(cls):  # type: (...) -> None
        Command.title(cls.CHECK_IMPORTS_TITLE)
        if CheckAllArgs.getinstance().skip_check_imports:
            scenario.logging.warning("Skipped")
        else:
            Command.execute([sys.executable, "tools/check-imports.py"])

    CHECK_SCHEMAS_TITLE = "Check JSON schemas"  # type: str

    @classmethod
    def _checkschemas(cls):  # type: (...) -> None
        Command.title(cls.CHECK_SCHEMAS_TITLE)
        if CheckAllArgs.getinstance().skip_check_schemas:
            scenario.logging.warning("Skipped")
        else:
            if CheckAllArgs.getinstance().full:
                Command.execute([sys.executable, "tools/check-schemas.py", "--validate-test-data", "--harden-schemas"])
            else:
                Command.execute([sys.executable, "tools/check-schemas.py", "--validate-test-data"])

    REQ_MGT_TITLE = "Update traceability"  # type: str

    @classmethod
    def _reqmgt(cls):  # type: (...) -> None
        Command.title(cls.REQ_MGT_TITLE)
        if CheckAllArgs.getinstance().skip_req_mgt:
            scenario.logging.warning("Skipped")
        else:
            Command.execute([sys.executable, "test/req-mgt.py"])

    CAMPAIGN_TITLE = "Unit test campaign"  # type: str

    @classmethod
    def _campaign(cls):  # type: (...) -> None
        Command.title(cls.CAMPAIGN_TITLE)
        if CheckAllArgs.getinstance().skip_campaign:
            scenario.logging.warning("Skipped")
        else:
            # Execute the campaign.
            _subdir_basename = scenario.datetime.toiso8601(time.time())[:len("XXXX-XX-XXTXX:XX:XX")].replace(":", "-").replace("T", "_")  # type: str
            Command.execute([sys.executable, "test/run-campaign.py", f"--outdir=test/results/{_subdir_basename}", "--subdir=none"])

            # Check campaign results.
            _errors = 0  # type: int
            _campaign_report_path = scenario.tools.paths.ROOT_SCENARIO_PATH / f"test/results/{_subdir_basename}/campaign.xml"  # type: scenario.Path
            for _line_number, _line in enumerate(_campaign_report_path.read_bytes().splitlines()):  # type: int, bytes
                if re.search(rb'status=.FAIL.', _line):
                    scenario.logging.debug("%s:%d: %r", _campaign_report_path, _line_number + 1, _line)
                    _errors += 1
            if _errors > 0:
                scenario.logging.error(f"{_errors} errors in '{_campaign_report_path}'")
                sys.exit(1)

    MKDOC_TITLE = "Generate documentation"  # type: str

    @classmethod
    def _mkdoc(cls):  # type: (...) -> None
        Command.title(cls.MKDOC_TITLE)
        if CheckAllArgs.getinstance().skip_mkdoc:
            scenario.logging.warning("Skipped")
        else:
            Command.execute([sys.executable, "tools/mkdoc.py"])


if __name__ == "__main__":
    # Command line arguments.
    scenario.Args.setinstance(CheckAllArgs())
    if not CheckAllArgs.getinstance().parse(sys.argv[1:]):
        sys.exit(int(CheckAllArgs.getinstance().error_code))

    scenario.Path.setmainpath(scenario.tools.paths.ROOT_SCENARIO_PATH)

    CheckAll.execute()
