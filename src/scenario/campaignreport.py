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
Campaign reports.
"""

import sys
import typing

# `CampaignExecution`, `TestCaseExecution` and `TestSuiteExecution` used in method signatures.
from .campaignexecution import CampaignExecution, TestCaseExecution, TestSuiteExecution
# `Logger` used for inheritance.
from .logger import Logger
# `Path` used in method signatures.
from .path import Path
# `Xml` used in method signatures.
from .xmlutils import Xml

if typing.TYPE_CHECKING:
    # `Path` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType


class CampaignReport(Logger):
    """
    Campaign report management.

    JUnit XML reporting file format:

    - Refer to: https://llg.cubic.org/docs/junit/ [CUBIC]
    - Other useful resource: https://stackoverflow.com/questions/442556/spec-for-junit-xml-output
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`CampaignReport` class.
        """
        from .debugclasses import DebugClass

        Logger.__init__(self, log_class=DebugClass.CAMPAIGN_REPORT)

        #: JUnit report path being written or read.
        self._junit_path = Path()  # type: Path

    def writejunitreport(
            self,
            campaign_execution,  # type: CampaignExecution
            junit_path,  # type: AnyPathType
    ):  # type: (...) -> bool
        """
        Generates a JUnit XML report output file.

        :param campaign_execution: Campaign execution to generate the report for.
        :param junit_path: Path to write the JUnit report into.
        :return: ``True`` for success, ``False`` otherwise.
        """
        from .loggermain import MAIN_LOGGER

        try:
            self.resetindentation()
            self.debug("Writing campaign results to JUnit report '%s'", junit_path)

            # Create an XML document.
            _xml_doc = Xml.Document()  # type: Xml.Document
            # Create the top <testsuites/> node.
            self._junit_path = Path(junit_path)
            _xml_doc.root = self._campaign2xml(_xml_doc, campaign_execution)

            # Generate the JUnit XML outfile.
            _xml_doc.write(junit_path)

            return True
        except Exception as _err:
            MAIN_LOGGER.error(f"Could not write JUnit report '{junit_path}': {_err}")
            self.debug("Exception", exc_info=sys.exc_info())
            return False
        finally:
            self.resetindentation()

    def readjunitreport(
            self,
            junit_path,  # type: AnyPathType
    ):  # type: (...) -> typing.Optional[CampaignExecution]
        """
        Reads the JUnit report.

        :param junit_path: Path of the JUnit file to read.
        :return:
            Campaign execution data read from the JUnit file.
            ``None`` when the file could not be read, or its content could not be parsed successfully.
        """
        from .loggermain import MAIN_LOGGER

        try:
            self.resetindentation()
            self.debug("Reading campaign results from JUnit report '%s'", junit_path)

            # Read and parse the JUnit XML file.
            _xml_doc = Xml.Document.read(junit_path)  # type: Xml.Document

            # Analyze the JSON content.
            self._junit_path = Path(junit_path)
            _campaign_execution = self._xml2campaign(_xml_doc)  # type: CampaignExecution

            return _campaign_execution
        except Exception as _err:
            MAIN_LOGGER.error(f"Could not read JUnit report '{junit_path}': {_err}")
            self.debug("Exception", exc_info=sys.exc_info())
            return None
        finally:
            self.resetindentation()

    def _campaign2xml(
            self,
            xml_doc,  # type: Xml.Document
            campaign_execution,  # type: CampaignExecution
    ):  # type: (...) -> Xml.Node
        """
        Campaign JUnit XML generation.

        :param xml_doc: XML document.
        :param campaign_execution: Campaign execution to generate the JUnit XML for.
        :return: Campaign JUnit XML.
        """
        # /testsuites top node:
        # [CUBIC]: "if only a single testsuite element is present, the testsuites element can be omitted. All attributes are optional."
        _xml_test_suites = xml_doc.createnode("testsuites")  # type: Xml.Node

        # /testsuites/@disabled:
        # [CUBIC]: "total number of disabled tests from all testsuites."
        _xml_test_suites.setattr("disabled", str(campaign_execution.counts.disabled))

        # /testsuites/@errors:
        # [CUBIC]: "total number of tests with error result from all testsuites."
        _xml_test_suites.setattr("errors", str(campaign_execution.counts.errors))

        # /testsuites/@failures:
        # [CUBIC]: "total number of failed tests from all testsuites."
        _xml_test_suites.setattr("failures", str(campaign_execution.counts.failures))

        # /testsuites/@name:
        # [CUBIC]: (No documentation)
        #          Seems to be optional from the XSD definition proposed.
        # _xml_test_suites.setattr("name", "")

        # /testsuites/@tests:
        # [CUBIC]: "total number of successful tests from all testsuites."
        # Weird as it does not match with the documentation for testsuite/@tests...
        # Lets' consider the actual meaning of this attribute is: 'The total number of tests in the test suite'
        _xml_test_suites.setattr("tests", str(campaign_execution.counts.total))

        # /testsuites/@time:
        # [CUBIC]: "time in seconds to execute all test suites."
        _xml_test_suites.setattr("time", str(campaign_execution.time.elapsed))

        # :mod:`scenario` statistic, non JUnit standard...
        _xml_test_suites.setattr("steps-executed", str(campaign_execution.steps.executed))
        _xml_test_suites.setattr("steps-total", str(campaign_execution.steps.total))
        _xml_test_suites.setattr("actions-executed", str(campaign_execution.actions.executed))
        _xml_test_suites.setattr("actions-total", str(campaign_execution.actions.total))
        _xml_test_suites.setattr("results-executed", str(campaign_execution.results.executed))
        _xml_test_suites.setattr("results-total", str(campaign_execution.results.total))

        # /testsuites/testsuite nodes:
        # [CUBIC]: "testsuite can appear multiple times, if contained in a testsuites element. It can also be the root element."
        _test_suite_id = 0  # type: int
        for _test_suite_execution in campaign_execution.test_suite_executions:  # type: TestSuiteExecution
            _xml_test_suites.appendchild(self._testsuite2xml(xml_doc, _test_suite_execution, _test_suite_id))
            _test_suite_id += 1

        return _xml_test_suites

    def _xml2campaign(
            self,
            xml_doc,  # type: Xml.Document
    ):  # type: (...) -> CampaignExecution
        """
        Campaign execution reading from JUnit report.

        :param xml_doc: JUnit XML document to read from.
        :return: Campaign execution data.
        """
        _campaign_execution = CampaignExecution(outdir=self._junit_path.parent)  # type: CampaignExecution

        _xml_test_suites = xml_doc.root  # type: Xml.Node
        assert _xml_test_suites.tag_name == "testsuites", "Root node should be a <testsuites/> node"

        if _xml_test_suites.hasattr("disabled"):
            _campaign_execution.counts.disabled = int(_xml_test_suites.getattr("disabled"))
            self.debug("testsuites/@disabled = %d", _campaign_execution.counts.disabled)
        if _xml_test_suites.hasattr("errors"):
            _campaign_execution.counts.errors = int(_xml_test_suites.getattr("errors"))
            self.debug("testsuites/@errors = %d", _campaign_execution.counts.errors)
        if _xml_test_suites.hasattr("failures"):
            _campaign_execution.counts.failures = int(_xml_test_suites.getattr("failures"))
            self.debug("testsuites/@failures = %d", _campaign_execution.counts.failures)
        if _xml_test_suites.hasattr("tests"):
            _campaign_execution.counts.total = int(_xml_test_suites.getattr("tests"))
            self.debug("testsuites/@tests = %d", _campaign_execution.counts.total)
        if _xml_test_suites.hasattr("time"):
            _campaign_execution.time.elapsed = float(_xml_test_suites.getattr("time"))
            self.debug("testsuites/@time = %f", _campaign_execution.time.elapsed)

        for _xml_test_suite in _xml_test_suites.getchildren("testsuite"):  # type: Xml.Node
            self.debug("New testsuites/testsuite")
            try:
                self.pushindentation()
                _campaign_execution.test_suite_executions.append(self._xml2testsuite(_campaign_execution, _xml_test_suite))
            finally:
                self.popindentation()

        # Eventually check the :mod:`scenario` statistic, which are properties of :class:`.campaignexecution.CampaignExecution`.
        self._xmlcheckstats(_xml_test_suites, "steps-executed", _campaign_execution.test_suite_executions)
        self._xmlcheckstats(_xml_test_suites, "steps-total", _campaign_execution.test_suite_executions)
        self._xmlcheckstats(_xml_test_suites, "actions-total", _campaign_execution.test_suite_executions)
        self._xmlcheckstats(_xml_test_suites, "actions-executed", _campaign_execution.test_suite_executions)
        self._xmlcheckstats(_xml_test_suites, "results-total", _campaign_execution.test_suite_executions)
        self._xmlcheckstats(_xml_test_suites, "results-executed", _campaign_execution.test_suite_executions)

        return _campaign_execution

    def _testsuite2xml(
            self,
            xml_doc,  # type: Xml.Document
            test_suite_execution,  # type: TestSuiteExecution
            test_suite_id,  # type: int
    ):  # type: (...) -> Xml.Node
        """
        Test suite JUnit XML generation.

        :param xml_doc: XML document.
        :param test_suite_execution: Test suite execution to generate the JUnit XML for.
        :param test_suite_id: Test suite identifier.
        :return: Test suite JUnit XML.
        """
        from .datetimeutils import toiso8601

        _xml_test_suite = xml_doc.createnode("testsuite")  # type: Xml.Node

        # testsuite/@name:
        # [CUBIC]: "Full (class) name of the test for non-aggregated testsuite documents. Class name without the package for aggregated testsuites documents.
        #           Required"
        self._path2xmlattr(_xml_test_suite, "name", test_suite_execution.test_suite_file.path)

        # testsuite/@tests:
        # [CUBIC]: "The total number of tests in the suite, required."
        _xml_test_suite.setattr("tests", str(test_suite_execution.counts.total))

        # testsuite/@disabled:
        # [CUBIC]: "the total number of disabled tests in the suite. optional"
        _xml_test_suite.setattr("disabled", str(test_suite_execution.counts.disabled))

        # testsuite/@errors:
        # [CUBIC]: "The total number of tests in the suite that errored. An errored test is one that had an unanticipated problem, for example an unchecked
        #           throwable; or a problem with the implementation of the test. optional"
        _xml_test_suite.setattr("errors", str(test_suite_execution.counts.errors))

        # testsuite/@failures:
        # [CUBIC]: "The total number of tests in the suite that failed. A failure is a test which the code has explicitly failed by using the mechanisms for
        #           that purpose. e.g., via an assertEquals. optional"
        _xml_test_suite.setattr("failures", str(test_suite_execution.counts.failures))

        # testsuite/@hostname:
        # [CUBIC]: "Host on which the tests were executed. 'localhost' should be used if the hostname cannot be determined. optional"
        # _xml_test_suite.setattr("hostname", "")

        # testsuite/@id:
        # [CUBIC]: "Starts at 0 for the first testsuite and is incremented by 1 for each following testsuite"
        _xml_test_suite.setattr("id", str(test_suite_id))

        # testsuite/@package:
        # [CUBIC]: "Derived from testsuite/@name in the non-aggregated documents. optional"
        # _xml_test_suite.setattr("package", "")

        # testsuite/@skipped:
        # [CUBIC]: "The total number of skipped tests. optional"
        _xml_test_suite.setattr("skipped", str(test_suite_execution.counts.skipped))

        # testsuite/@time:
        # [CUBIC]: "Time taken (in seconds) to execute the tests in the suite. optional"
        _xml_test_suite.setattr("time", str(test_suite_execution.time.elapsed))

        # testsuite/@timestamp:
        # [CUBIC]: "when the test was executed in ISO 8601 format (2014-01-21T16:17:18). Timezone may not be specified. optional"
        _xml_test_suite.setattr("timestamp", toiso8601(test_suite_execution.time.start) if test_suite_execution.time.start else "")

        # :mod:`scenario` statistic, non JUnit standard...
        _xml_test_suite.setattr("steps-executed", str(test_suite_execution.steps.executed))
        _xml_test_suite.setattr("steps-total", str(test_suite_execution.steps.total))
        _xml_test_suite.setattr("actions-executed", str(test_suite_execution.actions.executed))
        _xml_test_suite.setattr("actions-total", str(test_suite_execution.actions.total))
        _xml_test_suite.setattr("results-executed", str(test_suite_execution.results.executed))
        _xml_test_suite.setattr("results-total", str(test_suite_execution.results.total))

        # /testsuites/testsuite/testcase nodes:
        # [CUBIC]: "testcase can appear multiple times, see /testsuites/testsuite@tests"
        for _test_case_execution in test_suite_execution.test_case_executions:  # type: TestCaseExecution
            _xml_test_suite.appendchild(self._testcase2xml(xml_doc, _test_case_execution))

        # /testsuite/system-out:
        # [CUBIC]: "Data that was written to standard out while the test suite was executed. optional"

        # /testsuite/system-err:
        # [CUBIC]: "Data that was written to standard error while the test suite was executed. optional"

        return _xml_test_suite

    def _xml2testsuite(
            self,
            campaign_execution,  # type: CampaignExecution
            xml_test_suite,  # type: Xml.Node
    ):  # type: (...) -> TestSuiteExecution
        """
        Test suite reading from JUnit report.

        :param campaign_execution: Owner campaign execution instance.
        :param xml_test_suite: JUnit XML to read from.
        :return: Test suite execution data.
        """
        from .datetimeutils import f2strtime, fromiso8601, toiso8601
        from .debugutils import callback

        _test_suite_execution = TestSuiteExecution(campaign_execution, self._xmlattr2path(xml_test_suite, "name"))  # type: TestSuiteExecution

        if xml_test_suite.hasattr("tests"):
            _test_suite_execution.counts.total = int(xml_test_suite.getattr("tests"))
            self.debug("testsuite/@tests = %d", _test_suite_execution.counts.total)
        if xml_test_suite.hasattr("disabled"):
            _test_suite_execution.counts.disabled = int(xml_test_suite.getattr("disabled"))
            self.debug("testsuite/@disabled = %d", _test_suite_execution.counts.disabled)
        if xml_test_suite.hasattr("errors"):
            _test_suite_execution.counts.errors = int(xml_test_suite.getattr("errors"))
            self.debug("testsuite/@errors = %d", _test_suite_execution.counts.errors)
        if xml_test_suite.hasattr("failures"):
            _test_suite_execution.counts.failures = int(xml_test_suite.getattr("failures"))
            self.debug("testsuite/@failures = %d", _test_suite_execution.counts.failures)
        if xml_test_suite.hasattr("id"):
            _id = int(xml_test_suite.getattr("id"))  # type: int
            self.debug("testsuite/@id = %d", _id)
            if _id != len(campaign_execution.test_suite_executions):
                self.warning(f"Mismatching test suite id {_id}, should be {len(campaign_execution.test_suite_executions)}")
        if xml_test_suite.hasattr("skipped"):
            _test_suite_execution.counts.skipped = int(xml_test_suite.getattr("skipped"))
            self.debug("testsuite/@skipped = %d", _test_suite_execution.counts.skipped)
        if xml_test_suite.hasattr("time"):
            _test_suite_execution.time.elapsed = float(xml_test_suite.getattr("time"))
            self.debug("testsuite/@time = %f", _test_suite_execution.time.elapsed)
        if xml_test_suite.hasattr("timestamp"):
            _test_suite_execution.time.start = fromiso8601(xml_test_suite.getattr("timestamp"))
            self.debug("testsuite/@timestamp = %s", callback(f2strtime, _test_suite_execution.time.start))
            if _test_suite_execution.time.elapsed is not None:
                _test_suite_execution.time.end = _test_suite_execution.time.start + _test_suite_execution.time.elapsed
                self.debug("testsuite/@timestamp + elapsed => end = %s", callback(f2strtime, _test_suite_execution.time.end))

        for _xml_test_case in xml_test_suite.getchildren("testcase"):  # type: Xml.Node
            self.debug("New testsuite/testcase")
            try:
                self.pushindentation()
                _test_suite_execution.test_case_executions.append(self._xml2testcase(_test_suite_execution, _xml_test_case))
            finally:
                self.popindentation()

        # Eventually check the :mod:`scenario` statistic, which are properties of :class:`.campaignexecution.TestSuite`.
        self._xmlcheckstats(xml_test_suite, "steps-executed", _test_suite_execution.test_case_executions)
        self._xmlcheckstats(xml_test_suite, "steps-total", _test_suite_execution.test_case_executions)
        self._xmlcheckstats(xml_test_suite, "actions-total", _test_suite_execution.test_case_executions)
        self._xmlcheckstats(xml_test_suite, "actions-executed", _test_suite_execution.test_case_executions)
        self._xmlcheckstats(xml_test_suite, "results-total", _test_suite_execution.test_case_executions)
        self._xmlcheckstats(xml_test_suite, "results-executed", _test_suite_execution.test_case_executions)

        return _test_suite_execution

    def _testcase2xml(
            self,
            xml_doc,  # type: Xml.Document
            test_case_execution,  # type: TestCaseExecution
    ):  # type: (...) -> Xml.Node
        """
        Test case JUnit XML generation.

        :param xml_doc: XML document.
        :param test_case_execution: Test case execution to generate the JUnit XML for.
        :return: Test case JUnit XML.
        """
        from .knownissues import KnownIssue
        from .testerrors import ExceptionError, TestError

        _xml_test_case = xml_doc.createnode("testcase")  # type: Xml.Node

        # testcase/@name:
        # [CUBIC]: "Name of the test method, required."
        _xml_test_case.setattr("name", test_case_execution.name)

        # testcase/@assertions:
        # [CUBIC]: "number of assertions in the test case. optional"
        # _xml_test_case.setattr("assertions", "0")

        # testcase/@classname:
        # [CUBIC]: "Full class name for the class the test method is in. required"
        self._path2xmlattr(_xml_test_case, "classname", test_case_execution.script_path)

        # testcase/@status
        # [CUBIC]: "optional. not supported by maven surefire."
        _xml_test_case.setattr("status", str(test_case_execution.status))

        # testcase/@time
        # [CUBIC]: "Time taken (in seconds) to execute the test. optional"
        _xml_test_case.setattr("time", str(test_case_execution.time.elapsed))

        # :mod:`scenario` statistic, non JUnit standard...
        _xml_test_case.setattr("steps-executed", str(test_case_execution.steps.executed))
        _xml_test_case.setattr("steps-total", str(test_case_execution.steps.total))
        _xml_test_case.setattr("actions-executed", str(test_case_execution.actions.executed))
        _xml_test_case.setattr("actions-total", str(test_case_execution.actions.total))
        _xml_test_case.setattr("results-executed", str(test_case_execution.results.executed))
        _xml_test_case.setattr("results-total", str(test_case_execution.results.total))

        # Set references to the log and JSON outfiles.
        # Non JUnit standard...
        # Syntax inspired from HTML '<link rel="stylesheet" type="text/css" href=""/>' items.
        # testcase/link[@rel='log']:
        _xml_log_link = _xml_test_case.appendchild(xml_doc.createnode("link"))  # type: Xml.Node
        _xml_log_link.setattr("rel", "log")
        _xml_log_link.setattr("type", "text/plain")
        if test_case_execution.log.path is not None:
            self._path2xmlattr(_xml_log_link, "href", test_case_execution.log.path)
        # testcase/link[@rel='report']:
        _xml_json_link = _xml_test_case.appendchild(xml_doc.createnode("link"))  # type: Xml.Node
        _xml_json_link.setattr("rel", "report")
        _xml_json_link.setattr("type", "application/json")
        if test_case_execution.json.path is not None:
            self._path2xmlattr(_xml_json_link, "href", test_case_execution.json.path)

        # Create a <failure/> node for each test error.
        for _error in test_case_execution.errors:  # type: TestError
            # testcase/failure:
            # [CUBIC]: "failure indicates that the test failed. A failure is a test which the code has explicitly failed by using the mechanisms for that
            #           purpose. For example via an assertEquals. (...) optional"
            _xml_failure = _xml_test_case.appendchild(xml_doc.createnode("failure"))  # type: Xml.Node

            # testcase/failure/@message:
            # [CUBIC]: "# The message specified in the assert."
            if isinstance(_error, ExceptionError):
                # When this is an exception error, just give the message here, do not repeat the exception type,
                # which will be set in testcase/failure/@type.
                _xml_failure.setattr("message", _error.message)
            else:
                _xml_failure.setattr("message", str(_error))

            # testcase/failure/@type:
            # [CUBIC]: "# The type of the assert."
            if isinstance(_error, ExceptionError):
                _xml_failure.setattr("type", _error.exception_type)
            elif isinstance(_error, KnownIssue):
                _xml_failure.setattr("type", "known-issue")

            # testcase/failure/[text]:
            # [CUBIC]: "Contains as a text node relevant data for the failure, e.g., a stack trace."
            # Exception detail: put the log trailer
            _text = ""  # type: str
            if isinstance(_error, ExceptionError) and _error.exception:
                _text = "".join(_error.exception.format())
                _text += "\n"
            if _error.location:
                _text += f"{_error.location.tolongstring()}: {_error}"
            else:
                _text += f"{_error}"
            _xml_failure.appendchild(xml_doc.createtextnode(_text))

        # testcase/system-out:
        # [CUBIC]: "Data that was written to standard out while the test was executed. optional"
        if test_case_execution.log.content is not None:
            _xml_system_out = _xml_test_case.appendchild(xml_doc.createnode("system-out"))  # type: Xml.Node
            _xml_system_out.appendchild(xml_doc.createtextnode(self._safestr2xml(test_case_execution.log.content.decode("utf-8"))))

        # testcase/system-err:
        # [CUBIC]: "Data that was written to standard error while the test was executed. optional"

        return _xml_test_case

    def _xml2testcase(
            self,
            test_suite_execution,  # type: TestSuiteExecution
            xml_test_case,  # type: Xml.Node
    ):  # type: (...) -> TestCaseExecution
        """
        Test case reading from JUnit XML.

        :param test_suite_execution: Owner test suite execution instance.
        :param xml_test_case: JUnit XML to read from.
        :return: Test case execution data.
        """
        from .executionstatus import ExecutionStatus
        from .knownissues import KnownIssue
        from .locations import CodeLocation
        from .testerrors import ExceptionError, TestError

        # Note: The testcase/@name attribute is filled with the pretty path.
        #       The testcase/@classname attribute gives the full path.
        # _name = xml_test_case.getattr("name")  # type: str
        _script_path = self._xmlattr2path(xml_test_case, "classname")  # type: Path
        self.debug("testcase/@classname = '%s'", _script_path)

        _test_case_execution = TestCaseExecution(test_suite_execution, _script_path)  # type: TestCaseExecution

        if xml_test_case.hasattr("time"):
            _test_case_execution.time.elapsed = float(xml_test_case.getattr("time"))
            self.debug("testcase/@time = %f", _test_case_execution.time.elapsed)

        for _xml_link in xml_test_case.getchildren("link"):
            if _xml_link.getattr("rel") == "log":
                _test_case_execution.log.path = self._xmlattr2path(_xml_link, "href")
                self.debug("testcase/link[@rel='log']/@href = '%s'", _test_case_execution.log.path)
                # Read the log file by the way.
                _test_case_execution.log.read()
            if _xml_link.getattr("rel") == "report":
                _test_case_execution.json.path = self._xmlattr2path(_xml_link, "href")
                self.debug("testcase/link[@rel='report']/@href = '%s'", _test_case_execution.json.path)
                # Read the JSON report by the way.
                _test_case_execution.json.read()

        # Failures have already been filled by reading the JSON report above.
        # Let's reset them, and build them again (at the scenario level only), this time from the JUnit report information.
        if _test_case_execution.scenario_execution:
            _test_case_execution.scenario_execution.errors = []
            for _xml_failure in xml_test_case.getchildren("failure"):  # type: Xml.Node
                self.debug("New testcase/failure")
                if _xml_failure.hasattr("message") and _test_case_execution.scenario_execution:
                    _error = TestError(_xml_failure.getattr("message"))  # type: TestError
                    self.debug("testcase/failure/@message = %r", _error.message)
                    if _xml_failure.hasattr("type"):
                        if _xml_failure.getattr("type") == "known-issue":
                            self.debug("testcase/failure/@type = 'known-issue'")
                            _error = KnownIssue.fromstr(_error.message)
                            self.debug("testcase/failure/@message => %r", _error)
                        else:
                            _error = ExceptionError(exception=None)
                            _error.exception_type = _xml_failure.getattr("type")
                            self.debug("testcase/failure/@type = '%s'", _error.exception_type)
                            _error.message = _xml_failure.getattr("message")
                    for _xml_text in _xml_failure.gettextnodes():  # type: Xml.TextNode
                        _last_line = _xml_text.data.splitlines()[-1]  # type: str
                        if _last_line.count(":") >= 3:
                            _error.location = CodeLocation.fromlongstring(":".join(_last_line.split(":")[:3]))
                            self.debug("testcase/failure/@location = '%s'", _error.location.tolongstring())
                    _test_case_execution.scenario_execution.errors.append(_error)
        if xml_test_case.hasattr("status"):
            self.debug("testcase/@status = %r", xml_test_case.getattr("status"))
            if _test_case_execution.errors and (xml_test_case.getattr("status") != str(ExecutionStatus.FAIL)):
                self.warning(f"Mismatching status {xml_test_case.getattr('status')!r} with {len(_test_case_execution.errors)} error count")
            if (not _test_case_execution.errors) and (xml_test_case.getattr("status") == str(ExecutionStatus.FAIL)):
                self.warning(f"Mismatching status {xml_test_case.getattr('status')!r} while no error")

        if _test_case_execution.scenario_execution:
            # Check the :mod:`scenario` statistic, which are properties of :class:`.campaignexecution.TestCase`.
            self._xmlcheckstats(xml_test_case, "steps-executed", [_test_case_execution.scenario_execution])
            self._xmlcheckstats(xml_test_case, "steps-total", [_test_case_execution.scenario_execution])
            self._xmlcheckstats(xml_test_case, "actions-total", [_test_case_execution.scenario_execution])
            self._xmlcheckstats(xml_test_case, "actions-executed", [_test_case_execution.scenario_execution])
            self._xmlcheckstats(xml_test_case, "results-total", [_test_case_execution.scenario_execution])
            self._xmlcheckstats(xml_test_case, "results-executed", [_test_case_execution.scenario_execution])

        return _test_case_execution

    def _safestr2xml(
            self,
            string,  # type: str
    ):  # type: (...) -> str
        """
        Safe string conversion before it is used in the JUnit report.

        Removal of colors.

        :param string: String to convert.
        :return: String safely converted.
        """
        from .logformatter import LogFormatter

        return LogFormatter.nocolor(string)

    def _path2xmlattr(
            self,
            xml_node,  # type: Xml.Node
            attr_name,  # type: str
            path,  # type: Path
    ):  # type: (...) -> None
        """
        Sets a path XML attribute.

        Sets either a relative or absolute path
        depending on the given file location compared with this JUnit file location.

        :param xml_node: XML node to set the attribute for.
        :param attr_name: Attribute name.
        :param path: Path object to use to set the attribute value.
        """
        _main_path = Path.getmainpath() or Path.cwd()  # type: Path
        if path.is_relative_to(_main_path):
            xml_node.setattr(attr_name, path.relative_to(_main_path))
        else:
            xml_node.setattr(attr_name, path.abspath)

    def _xmlattr2path(
            self,
            xml_node,  # type: Xml.Node
            attr_name,  # type: str
    ):  # type: (...) -> Path
        """
        Path computation from an XML attribute.

        When the attribute describes a relative path, the path is computed from the JUnit file.
        When it describes an absolute path, the path is taken as is.

        :param xml_node: XML node which attribute to read from.
        :param attr_name: Attribute name to read.
        :return: Path computed.
        """
        return Path(xml_node.getattr(attr_name), relative_to=Path.getmainpath() or Path.cwd())

    def _xmlcheckstats(
            self,
            xml_node,  # type: Xml.Node
            attr_name,  # type: str
            objects,  # type: typing.List[typing.Any]
    ):  # type: (...) -> None
        """
        Statistics consistency checking between an upper level and its children.

        :param xml_node: Upper XML node which statistics to check.
        :param attr_name: Statistics attribute to check.
        :param objects: Execution objects to check statistics with.

        Displays warnings when the statistics mismatch.
        """
        from .scenarioexecution import ScenarioExecution

        assert attr_name.count("-") == 1
        _stat_type, _exec_total = attr_name.split("-")  # type: str, str
        if xml_node.hasattr(attr_name):
            _top_count = int(xml_node.getattr(attr_name))  # type: int
            _sum = 0  # type int
            _object_type = ""  # type: str
            for _object in objects:
                _object_type = type(_object).__name__ + " "
                if isinstance(_object, ScenarioExecution):
                    _sum += getattr(getattr(_object, _stat_type[:-1] + "_stats"), _exec_total)
                elif isinstance(_object, (TestSuiteExecution, TestCaseExecution)):
                    _sum += getattr(getattr(_object, _stat_type), _exec_total)
            if _top_count != _sum:
                self.warning(f"Mismatching @{attr_name} counts between <{xml_node.tag_name}/> (count={_top_count}) and {_object_type}sub-objects (sum={_sum})")


__doc__ += """
.. py:attribute:: CAMPAIGN_REPORT

    Main instance of :class:`CampaignReport`.
"""
CAMPAIGN_REPORT = CampaignReport()  # type: CampaignReport
