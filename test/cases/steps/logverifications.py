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

import typing

import scenario
import scenario.test
import scenario.text

if True:
    from steps.logprocessing import LogProcessor as _LogProcessorImpl  # `LogProcessor` used for inheritance.


class LogVerificationStep(scenario.test.VerificationStep, _LogProcessorImpl):
    """
    Base step that facilitates analyses of the log output.
    """

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            encoding=None,  # type: str
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)
        _LogProcessorImpl.__init__(self, encoding)

    def _findlines(
            self,
            searched,  # type: typing.AnyStr
            output=None,  # type: typing.AnyStr
            find_all=True,  # type: bool
    ):  # type: (...) -> typing.List[typing.AnyStr]
        _lines = []  # type: typing.List[typing.AnyStr]
        if output is None:
            output = self.toanystr(self.subprocess.stdout, type(searched))
        for _line in output.splitlines():  # type: typing.AnyStr
            if searched in _line:
                _lines.append(_line)
                if not find_all:
                    break
        return _lines

    def assertline(
            self,
            searched,  # type: typing.AnyStr
            output=None,  # type: typing.AnyStr
            evidence=False,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> typing.AnyStr
        from .commonargs import ExecCommonArgs

        _lines = self._findlines(searched, output, find_all=False)  # type: typing.List[typing.AnyStr]
        self.assertisnotempty(
            _lines,
            err=scenario.debug.FmtAndArgs(
                "No such line %s in %s execution output",
                scenario.debug.saferepr(searched), self.getexecstep(ExecCommonArgs).listpaths(),
            ),
        )
        scenario.assertionhelpers.evidence(
            evidence,
            "%s found in %s execution output",
            scenario.debug.saferepr(searched), self.getexecstep(ExecCommonArgs).listpaths(),
        )
        return _lines[0]

    def assertlines(
            self,
            searched,  # type: typing.AnyStr
            output=None,  # type: typing.AnyStr
            evidence=False,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> typing.List[typing.AnyStr]
        from .commonargs import ExecCommonArgs

        _lines = self._findlines(searched, output)  # type: typing.List[typing.AnyStr]
        self.assertisnotempty(
            _lines,
            err=scenario.debug.FmtAndArgs(
                "No such line %s in %s execution output",
                scenario.debug.saferepr(searched), self.getexecstep(ExecCommonArgs).listpaths(),
            ),
        )
        scenario.assertionhelpers.evidence(
            evidence,
            "%s found %s in %s execution output",
            scenario.debug.saferepr(searched), scenario.text.adverbial(len(_lines)), self.getexecstep(ExecCommonArgs).listpaths(),
        )
        return _lines

    def assertnoline(
            self,
            searched,  # type: typing.AnyStr
            output=None,  # type: typing.AnyStr
            evidence=False,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        from .commonargs import ExecCommonArgs

        for _line in self._findlines(searched, output):  # type: typing.AnyStr
            # The following assertion should always fail in as much as the line matches the `searched` pattern.
            # Nevertheless, we call `assertnotin()` on each line instead of `assertisempty()` on the list,
            # in order to produce more detailed error messages in case of an error.
            self.assertnotin(searched, _line)
        scenario.assertionhelpers.evidence(
            evidence,
            "No such line %s in %s execution output",
            scenario.debug.saferepr(searched), self.getexecstep(ExecCommonArgs).listpaths(),
        )

    def assertlinecount(
            self,
            searched,  # type: typing.AnyStr
            count,  # type: int
            output=None,  # type: typing.AnyStr
            evidence=False,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> typing.List[typing.AnyStr]
        from .commonargs import ExecCommonArgs

        _lines = self._findlines(searched, output)  # type: typing.List[typing.AnyStr]
        self.assertlen(
            _lines, count,
            err=scenario.debug.FmtAndArgs(
                "%s found %s in %s execution output (%s expected)",
                scenario.debug.saferepr(searched), scenario.text.adverbial(len(_lines)), self.getexecstep(ExecCommonArgs).listpaths(),
                scenario.text.adverbial(count),
            ),
        )
        scenario.assertionhelpers.evidence(
            evidence,
            "%s found %s in %s execution output",
            scenario.debug.saferepr(searched), scenario.text.adverbial(len(_lines)), self.getexecstep(ExecCommonArgs).listpaths(),
        )
        return _lines

    def assertcolor(
            self,
            line,  # type: typing.AnyStr
            text,  # type: typing.AnyStr
            color,  # type: scenario.Console.Color
            evidence=False,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        _type = type(line)  # type: typing.Type[typing.AnyStr]
        _colored_text = self.toanystr("", _type).join([
            self.toanystr(f"\033[{int(color)}m", _type),
            text,
            self.toanystr(f"\033[{int(scenario.Console.Color.RESET)}m", _type),
        ])  # type: typing.AnyStr
        self.assertin(_colored_text, line, evidence=evidence)

    def assertnocolor(
            self,
            line,  # type: typing.AnyStr
            evidence=False,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        self.assertnotin(self.toanystr("\033", type(line)), line, evidence=evidence)
