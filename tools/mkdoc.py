#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

import logging
import pathlib
import sys

# Path management.
MAIN_PATH = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(MAIN_PATH / "src"))
sys.path.append(str(MAIN_PATH / "tools" / "src"))

# :mod:`scenario` imports.
import scenario.tools  # noqa: E402  ## Module level import not at top of file


class MkDoc:

    PLANTUML_PATH = scenario.tools.paths.TOOLS_LIB_PATH / "plantuml.1.2020.15.jar"  # type: scenario.Path

    def run(self):  # type: (...) -> None

        # Command line arguments.
        scenario.Args.setinstance(scenario.Args(class_debugging=False))
        scenario.Args.getinstance().setdescription("Documentation generation.")
        if not scenario.Args.getinstance().parse(sys.argv[1:]):
            sys.exit(int(scenario.Args.getinstance().error_code))

        scenario.Path.setmainpath(scenario.tools.paths.MAIN_PATH)
        self.checktools()
        self.buildlogs()
        self.builddiagrams()
        self.sphinxapidoc()
        self.sphinxbuild()

    def checktools(self):  # type: (...) -> None
        scenario.tools.checkthirdpartytoolversion("sphinx-apidoc", ["sphinx-apidoc", "--version"])
        scenario.tools.checkthirdpartytoolversion("sphinx-build", ["sphinx-build", "--version"])
        # tools.checkthirdpartytoolversion("dot", ["dot", "-V"])  ## PlantUML does not need dot to be installed for regular sequence diagrams.
        scenario.tools.checkthirdpartytoolversion("java", ["java", "-version"])
        scenario.tools.checkthirdpartytoolversion("PlantUML", ["java", "-jar", self.PLANTUML_PATH, "-version"], cwd=scenario.tools.paths.MAIN_PATH)

    def buildlogs(self):  # type: (...) -> None
        """
        Updates the documentation data files.

        Ensures the sample execution times do not fluctuate in the output documentation from build to build.
        """
        _gen = scenario.tools.LogGenerator(scenario.tools.paths.DOC_DATA_PATH)  # type: scenario.tools.LogGenerator

        # Help logs.
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-test.py", options=["--help"],
            suffix=".help",
        )
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-campaign.py", options=["--help"],
            suffix=".help",
        )
        _gen.execute(
            scenario.tools.paths.DEMO_PATH / "run-demo.py", options=["--help"],
            suffix=".help",
        )

        # Scenario executions.
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-test.py",
            positionals=[scenario.tools.paths.DEMO_PATH / "commutativeaddition.py"],
            json_report=True,
        )
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-test.py",
            positionals=[scenario.tools.paths.DEMO_PATH / "commutativeadditions.py"],
            json_report=True,
        )
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-test.py",
            positionals=[scenario.tools.paths.DEMO_PATH / "loggingdemo.py"],
            json_report=True,
        )
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-test.py",
            positionals=[scenario.tools.paths.DEMO_PATH / "commutativeaddition.py", scenario.tools.paths.DEMO_PATH / "loggingdemo.py"],
            summary=True,
        )
        _gen.execute(
            scenario.tools.paths.DEMO_PATH / "run-demo.py", options=[
                "--config-file", scenario.tools.paths.DEMO_PATH / "conf.json",
                "--config-value", "x.y[0].z", "0",
                "--show-configs",
                scenario.tools.paths.DEMO_PATH / "htmllogin.py",
            ],
            suffix=".show-configs",
        )
        if (scenario.tools.paths.DEMO_PATH / "htmllogin.log").exists():
            (scenario.tools.paths.DEMO_PATH / "htmllogin.log").unlink()

        # Campaign executions.
        _gen.execute(
            scenario.tools.paths.BIN_PATH / "run-campaign.py", positionals=[scenario.tools.paths.DEMO_PATH / "demo.suite"],
            suffix=".campaign", summary=True, xml_report=True,
        )

        # Import dependencies.
        _gen.execute(scenario.tools.paths.MAIN_PATH / "tools" / "checkdeps.py")

    def builddiagrams(self):  # type: (...) -> None
        _cfg_path = scenario.tools.paths.DOC_SRC_PATH / "uml" / "umlconf.uml"  # type: scenario.Path
        for _path in (scenario.tools.paths.DOC_SRC_PATH / "uml").iterdir():  # type: scenario.Path
            if _path.is_file() and _path.name.endswith(".uml") and (not _path.samefile(_cfg_path)):
                _png_outpath = _path.parent / _path.name.replace(".uml", ".png")  # type: scenario.Path
                if scenario.tools.shouldupdate(_png_outpath, [_path, _cfg_path]):
                    scenario.logging.info(f"Generating {_png_outpath} from {_path}")
                    _subprocess = scenario.tools.SubProcess("java", "-jar", self.PLANTUML_PATH)  # type: scenario.tools.SubProcess
                    _subprocess.addargs("-config", _cfg_path)
                    _subprocess.addargs(_path)
                    _subprocess.setcwd(scenario.tools.paths.MAIN_PATH)
                    _subprocess.run()
                else:
                    scenario.logging.info(f"No need to update {_png_outpath} from {_path}")

    def sphinxapidoc(self):  # type: (...) -> None
        """
        Sphinx-apidoc execution: build .rst source files from the python sources.

        Useful options:
          -o DESTDIR, --output-dir DESTDIR = directory to place all output
          -f, --force = overwrite existing files
                        => apparently, does not ensure an update of the output file timestamps,
                           thus the `touch` line prior to `sphinx-build` still needs to be done.
          -e, --separate = put documentation for each module on its own page
          --tocfile TOCFILE = filename of table of contents (default: modules)
          -T, --no-toc = don't create a table of contents file
          --implicit-namespaces = interpret module paths according to PEP-0420 implicit namespaces specification
          -M, --module-first = put module documentation before submodule documentation
          -H HEADER, --doc-project HEADER = project name (default: root module name)
          -t TEMPLATEDIR, --templatedir TEMPLATEDIR = template directory for template files
          -q = no output on stdout, just warnings on stderr
          --ext-autodoc = enable autodoc extension
                          Not sure about what this option actually does...
        """
        # First remove the previous .rst files, in case a source module has been renamed.
        if (scenario.tools.paths.DOC_SRC_PATH / "py").is_dir():
            for _py_src_file in (scenario.tools.paths.DOC_SRC_PATH / "py").iterdir():  # type: scenario.Path
                if _py_src_file.name.endswith(".rst"):
                    scenario.logging.info(f"Removing file {_py_src_file}")
                    _py_src_file.unlink()

        scenario.logging.info("Executing sphinx-apidoc...")
        _subprocess = scenario.tools.SubProcess("sphinx-apidoc")  # type: scenario.tools.SubProcess
        _subprocess.addargs("--output-dir", scenario.tools.paths.DOC_SRC_PATH / "py")
        _subprocess.addargs("--force", "--module-first", "--separate")
        _subprocess.addargs(scenario.tools.paths.SRC_PATH / "scenario")
        _subprocess.setcwd(scenario.tools.paths.MAIN_PATH)
        _subprocess.run()

    def sphinxbuild(self):  # type: (...) -> None
        """
        Sphinx-build execution: build the sphinx documentation.

        Useful options:
          -b buildername = The most important option: it selects a builder.
          -a = write all files (default: only write new and changed files)
          -n = nit-picky mode, warn about all missing references
               => Generates tons of false errors, due to typings that sphinx does not handle correctly. Do not use.
          -W = turn warnings into errors
          --color = do emit colored output (default: auto-detect)
          -q = no output on stdout, just warnings on stderr
          -v = increase verbosity (can be repeated)
          -T = show full traceback on exception
        """
        scenario.logging.info("Executing sphinx-build...")

        scenario.logging.debug("Ensuring every .rst file timestamp has been updated")
        for _dir in (scenario.tools.paths.DOC_SRC_PATH, scenario.tools.paths.DOC_SRC_PATH / "py"):  # type: scenario.Path
            for _path in _dir.iterdir():  # type: scenario.Path
                if _path.is_file() and _path.name.endswith(".rst"):
                    scenario.logging.debug("%r.touch()", _path)
                    _path.touch()

        # Prepare the $(sphinx-build) process.
        _subprocess = scenario.tools.SubProcess("sphinx-build")  # type: scenario.tools.SubProcess
        # Debug & display:
        if scenario.Args.getinstance().debug_main:
            _subprocess.addargs("-vv")
        _subprocess.addargs("--color")
        # Builder:
        _subprocess.addargs("-b", "html")
        # Write all files:
        _subprocess.addargs("-a")
        # Configuration file:
        _subprocess.addargs("-c", scenario.tools.paths.TOOLS_CONF_PATH / "sphinx")
        # Source directory:
        _subprocess.addargs(scenario.tools.paths.DOC_SRC_PATH)
        # Output directory:
        _subprocess.addargs(scenario.tools.paths.DOC_OUT_PATH)

        # $(sphinx-build) execution.
        def _onstderrline(line):  # type: (bytes) -> None
            _level = logging.ERROR  # type: int
            if b'TODO entry found:' in line:
                # Just warn on todos.
                _level = logging.WARNING
            elif b'WARNING: duplicate object description' in line:
                # Just debug dublicate object warnings.
                _level = logging.DEBUG
            scenario.logging.log(_level, line.decode("utf-8"))
        _subprocess.onstderrline(_onstderrline)
        _subprocess.setcwd(scenario.tools.paths.MAIN_PATH)
        _subprocess.run()


if __name__ == "__main__":
    MkDoc().run()
