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

import typing

if True:
    from ._debugutils import callback as _callback  # `callback()` imported once for performance concerns.
    from ._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._campaignexecution import CampaignExecution as _CampaignExecutionType
    from ._campaignexecution import TestCaseExecution as _TestCaseExecutionType
    from ._campaignexecution import TestSuiteExecution as _TestSuiteExecutionType
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType
    from ._scenarioexecution import ScenarioExecution as _ScenarioExecutionType
    from ._xmlutils import Xml as _XmlType


if typing.TYPE_CHECKING:
    #: Any object type that provide statistics.
    _StatObjectType = typing.Union[
        _CampaignExecutionType,
        _TestSuiteExecutionType,
        _TestCaseExecutionType,
        _ScenarioExecutionType,
    ]


class CampaignReport(_LoggerImpl):
    """
    Campaign report management.

    Instantiated once with the :data:`CAMPAIGN_REPORT` singleton.

    JUnit XML reporting file format:

    - Refer to: https://llg.cubic.org/docs/junit/ [CUBIC]
    - Other useful resource: https://stackoverflow.com/questions/442556/spec-for-junit-xml-output
    """

    class LinkPurpose(_StrEnumImpl):
        """
        ``<link/>`` reference purposes.
        """
        #: Requirement database file link.
        REQ_DB = "req-db"
        #: Downstream traceability file link.
        DOWNSTREAM_TRACEABILITY = "req-downstream-traceability"
        #: Upstream traceability file link.
        UPSTREAM_TRACEABILITY = "req-upstream-traceability"
        #: Scenario log file link.
        SCENARIO_LOG = "log"
        #: Scenario report file link.
        SCENARIO_REPORT = "report"

    class StatAttrName(_StrEnumImpl):
        """
        `scenario` specific attribute names for statistics.
        """
        #: Number of steps executed.
        STEPS_EXECUTED = "steps-executed"
        #: Total number of steps.
        STEPS_TOTAL = "steps-total"
        #: Number of actions executed.
        ACTIONS_EXECUTED = "actions-executed"
        #: Total number of actions.
        ACTIONS_TOTAL = "actions-total"
        #: Number of expected results executed.
        RESULTS_EXECUTED = "results-executed"
        #: Total number of expected results.
        RESULTS_TOTAL = "results-total"

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`CampaignReport` class.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.CAMPAIGN_REPORT)

        #: Campaign report path being written or read.
        self._report_path = _PathImpl()  # type: _PathType

        #: Flag set to ``True`` when the requirement database should be fed with the requirement database file read from campaign results.
        self._feed_req_db = False  # type: bool
        #: Flag set to ``True`` when scenario log files should be automatically read.
        self._read_scenario_logs = False  # type: bool
        #: Falg set to ``True`` when scenario report files should be automatically read.
        self._read_scenario_reports = False  # type: bool

    def writejunitreport(
            self,
            campaign_execution,  # type: _CampaignExecutionType
            junit_path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        """
        Deprecated.
        Use :meth:`writecampaignreport()` instead.
        """
        self.warning("CampaignReport.writejunitreport() deprecated, please use CampaignReport.writecampaignreport() instead")
        try:
            self.writecampaignreport(
                campaign_execution,
                junit_path,
            )
            return True
        except Exception as _err:
            self.error(f"Could not write report '{junit_path}': {_err}")
            self.logexceptiontraceback(_err)
            return False

    def writecampaignreport(
            self,
            campaign_execution,  # type: _CampaignExecutionType
            report_path,  # type: _AnyPathType
    ):  # type: (...) -> None
        """
        Generates a JUnit XML campaign report file.

        :param campaign_execution: Campaign execution to generate the report for.
        :param report_path: Path to write the campaign report into.
        """
        from ._xmlutils import Xml

        try:
            self.resetindentation()
            self.debug("Writing campaign results to report '%s'", report_path)

            # Create an XML document.
            _xml_doc = Xml.Document()  # type: Xml.Document
            # Create the top <testsuites/> node.
            self._report_path = _PathImpl(report_path)
            _xml_doc.root = self._campaign2xml(_xml_doc, campaign_execution)

            # Generate the JUnit XML outfile.
            _xml_doc.writefile(self._report_path)
        finally:
            # Reset logging indentation and member variables.
            self.resetindentation()
            self._report_path = _PathImpl()

    def readjunitreport(
            self,
            junit_path,  # type: _AnyPathType
    ):  # type: (...) -> typing.Optional[_CampaignExecutionType]
        """
        Deprecated.
        Use :meth:`readcampaignreport()` instead.
        """
        self.warning(f"CampaignReport.readjunitreport() deprecated, please use CampaignReport.readcampaignreport() instead")
        try:
            return self.readcampaignreport(
                junit_path,
                feed_req_db=False,
                read_scenario_logs=True,
                read_scenario_reports=True,
            )
        except Exception as _err:
            self.error(f"Could not read report '{junit_path}': {_err}")
            self.logexceptiontraceback(_err)
            return None

    def readcampaignreport(
            self,
            report_path,  # type: _AnyPathType
            *,
            feed_req_db=False,  # type: bool
            read_scenario_logs=False,  # type: bool
            read_scenario_reports=False,  # type: bool
    ):  # type: (...) -> _CampaignExecutionType
        """
        Reads a JUnit XML campaign report file.

        :param report_path:
            Path of the campaign report file to read.
        :param feed_req_db:
            ``True`` to feed automatically the requirement database with verified requirement references.
        :param read_scenario_logs:
            ``True`` to read automatically scenario log files.
        :param read_scenario_reports:
            ``True`` to read automatically scenario report files.
        :return:
            Campaign execution data read from the JUnit file.
        """
        from ._xmlutils import Xml

        try:
            self.resetindentation()
            self.debug("Reading campaign results from report '%s'", report_path)

            # Read and parse the JUnit XML file.
            self._report_path = _PathImpl(report_path)
            _xml_doc = Xml.Document.readfile(self._report_path)  # type: Xml.Document

            # Analyze the JUnit XML content.
            self._feed_req_db = feed_req_db
            self._read_scenario_logs = read_scenario_logs
            self._read_scenario_reports = read_scenario_reports
            _campaign_execution = self._xml2campaign(_xml_doc)  # type: _CampaignExecutionType

            return _campaign_execution
        finally:
            # Reset logging indentation and member variables.
            self.resetindentation()
            self._report_path = _PathImpl()
            self._feed_req_db = False
            self._read_scenario_logs = False
            self._read_scenario_reports = False

    def _campaign2xml(
            self,
            xml_doc,  # type: _XmlType.Document
            campaign_execution,  # type: _CampaignExecutionType
    ):  # type: (...) -> _XmlType.Node
        """
        Campaign JUnit XML generation.

        :param xml_doc: XML document.
        :param campaign_execution: Campaign execution to generate the JUnit XML for.
        :return: Campaign JUnit XML.
        """
        from ._xmlutils import Xml

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

        # `scenario` statistics, non JUnit standard...
        self._objectstats2xmlattr(_xml_test_suites, campaign_execution)

        # /testsuites/link nodes (note: non JUnit standard):
        # /testsuites/link[@rel='req-db']:
        if campaign_execution.req_db_path.is_file():
            _xml_req_db_link = _xml_test_suites.appendchild(self._path2xmllink(
                xml_doc,
                campaign_execution.req_db_path,
                CampaignReport.LinkPurpose.REQ_DB,
            ))  # type: Xml.Node
        # /testsuites/link[@rel='req-downstream-traceability']:
        if campaign_execution.downstream_traceability_path.is_file():
            _xml_downstream_traceability = _xml_test_suites.appendchild(self._path2xmllink(
                xml_doc,
                campaign_execution.downstream_traceability_path,
                CampaignReport.LinkPurpose.DOWNSTREAM_TRACEABILITY,
            ))  # type: Xml.Node
        # /testsuites/link[@rel='req-upstream-traceability']:
        if campaign_execution.upstream_traceability_path.is_file():
            _xml_upstream_traceability = _xml_test_suites.appendchild(self._path2xmllink(
                xml_doc,
                campaign_execution.upstream_traceability_path,
                CampaignReport.LinkPurpose.UPSTREAM_TRACEABILITY,
            ))  # type: Xml.Node

        # /testsuites/testsuite nodes:
        # [CUBIC]: "testsuite can appear multiple times, if contained in a testsuites element. It can also be the root element."
        _test_suite_id = 0  # type: int
        for _test_suite_execution in campaign_execution.test_suite_executions:  # type: _TestSuiteExecutionType
            _xml_test_suites.appendchild(self._testsuite2xml(xml_doc, _test_suite_execution, _test_suite_id))
            _test_suite_id += 1

        return _xml_test_suites

    def _xml2campaign(
            self,
            xml_doc,  # type: _XmlType.Document
    ):  # type: (...) -> _CampaignExecutionType
        """
        Campaign execution reading from JUnit report.

        :param xml_doc: JUnit XML document to read from.
        :return: Campaign execution data.
        """
        from ._campaignexecution import CampaignExecution
        from ._xmlutils import Xml

        _campaign_execution = CampaignExecution(outdir=self._report_path.parent)  # type: CampaignExecution
        _campaign_execution.campaign_report_path = self._report_path

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

        for _xml_link in _xml_test_suites.getchildren("link"):  # type: Xml.Node
            _link_purpose = _xml_link.getattr("rel")  # type: str
            if _link_purpose == CampaignReport.LinkPurpose.REQ_DB:
                _campaign_execution.req_db_path = self._xmlattr2path(_xml_link, "href")
                self.debug("testsuites/link[@rel=%r]/@href = '%s'", _link_purpose, _campaign_execution.req_db_path)
                if self._feed_req_db:
                    # Read the requirement database file by the way.
                    self.debug("Feeding requirement database from '%s'", _campaign_execution.req_db_path)
                    _FAST_PATH.req_db.load(_campaign_execution.req_db_path)
            elif _link_purpose == CampaignReport.LinkPurpose.DOWNSTREAM_TRACEABILITY:
                _campaign_execution.downstream_traceability_path = self._xmlattr2path(_xml_link, "href")
                self.debug("testsuites/link[@rel=%r]/@href = '%s'", _link_purpose, _campaign_execution.downstream_traceability_path)
            elif _link_purpose == CampaignReport.LinkPurpose.UPSTREAM_TRACEABILITY:
                _campaign_execution.upstream_traceability_path = self._xmlattr2path(_xml_link, "href")
                self.debug("testsuites/link[@rel=%r]/@href = '%s'", _link_purpose, _campaign_execution.upstream_traceability_path)
            else:
                self.warning(f"Unknown testsuites/link/@rel value {_link_purpose!r}")

        for _xml_test_suite in _xml_test_suites.getchildren("testsuite"):  # type: Xml.Node
            self.debug("New testsuites/testsuite")
            with self.pushindentation():
                _campaign_execution.test_suite_executions.append(self._xml2testsuite(_campaign_execution, _xml_test_suite))

        # Eventually check the `scenario` statistics, which are properties of `CampaignExecution`.
        self._xmlcheckstats(self._report_path.prettypath, _xml_test_suites, _campaign_execution.test_suite_executions)

        return _campaign_execution

    def _testsuite2xml(
            self,
            xml_doc,  # type: _XmlType.Document
            test_suite_execution,  # type: _TestSuiteExecutionType
            test_suite_id,  # type: int
    ):  # type: (...) -> _XmlType.Node
        """
        Test suite JUnit XML generation.

        :param xml_doc: XML document.
        :param test_suite_execution: Test suite execution to generate the JUnit XML for.
        :param test_suite_id: Test suite identifier.
        :return: Test suite JUnit XML.
        """
        from ._datetimeutils import toiso8601
        from ._xmlutils import Xml

        _xml_test_suite = xml_doc.createnode("testsuite")  # type: Xml.Node

        # testsuite/@name:
        # [CUBIC]: "Full (class) name of the test for non-aggregated testsuite documents. Class name without the package for aggregated testsuites documents.
        #           Required"
        # Only field where we can give the test suite path.
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

        # `scenario` statistics, non JUnit standard...
        self._objectstats2xmlattr(_xml_test_suite, test_suite_execution)

        # /testsuites/testsuite/testcase nodes:
        # [CUBIC]: "testcase can appear multiple times, see /testsuites/testsuite@tests"
        for _test_case_execution in test_suite_execution.test_case_executions:  # type: _TestCaseExecutionType
            _xml_test_suite.appendchild(self._testcase2xml(xml_doc, _test_case_execution))

        # /testsuite/system-out:
        # [CUBIC]: "Data that was written to standard out while the test suite was executed. optional"

        # /testsuite/system-err:
        # [CUBIC]: "Data that was written to standard error while the test suite was executed. optional"

        return _xml_test_suite

    def _xml2testsuite(
            self,
            campaign_execution,  # type: _CampaignExecutionType
            xml_test_suite,  # type: _XmlType.Node
    ):  # type: (...) -> _TestSuiteExecutionType
        """
        Test suite reading from JUnit report.

        :param campaign_execution: Owner campaign execution instance.
        :param xml_test_suite: JUnit XML to read from.
        :return: Test suite execution data.
        """
        from ._campaignexecution import TestSuiteExecution
        from ._datetimeutils import f2strtime, fromiso8601
        from ._xmlutils import Xml

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
            self.debug("testsuite/@timestamp = %s", _callback(f2strtime, _test_suite_execution.time.start))
            if _test_suite_execution.time.elapsed is not None:
                _test_suite_execution.time.end = _test_suite_execution.time.start + _test_suite_execution.time.elapsed
                self.debug("testsuite/@timestamp + elapsed => end = %s", _callback(f2strtime, _test_suite_execution.time.end))

        for _xml_test_case in xml_test_suite.getchildren("testcase"):  # type: Xml.Node
            self.debug("New testsuite/testcase")
            with self.pushindentation():
                _test_suite_execution.test_case_executions.append(self._xml2testcase(_test_suite_execution, _xml_test_case))

        # Eventually check the `scenario` statistics, which are properties of `TestSuite`.
        self._xmlcheckstats(_test_suite_execution.name, xml_test_suite, _test_suite_execution.test_case_executions)

        return _test_suite_execution

    def _testcase2xml(
            self,
            xml_doc,  # type: _XmlType.Document
            test_case_execution,  # type: _TestCaseExecutionType
    ):  # type: (...) -> _XmlType.Node
        """
        Test case JUnit XML generation.

        :param xml_doc: XML document.
        :param test_case_execution: Test case execution to generate the JUnit XML for.
        :return: Test case JUnit XML.
        """
        from ._knownissues import KnownIssue
        from ._testerrors import ExceptionError, TestError
        from ._xmlutils import Xml

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

        # `scenario` statistics, non JUnit standard...
        self._objectstats2xmlattr(_xml_test_case, test_case_execution)

        # Set references to the log and scenario report outfiles (note: non JUnit standard).
        # testcase/link[@rel='log']:
        if test_case_execution.log.path and test_case_execution.log.path.is_file():
            _xml_log_link = _xml_test_case.appendchild(self._path2xmllink(
                xml_doc,
                test_case_execution.log.path,
                rel=CampaignReport.LinkPurpose.SCENARIO_LOG,
            ))  # type: Xml.Node
        # testcase/link[@rel='report']:
        if test_case_execution.report.path is not None:
            _xml_report_link = _xml_test_case.appendchild(self._path2xmllink(
                xml_doc,
                test_case_execution.report.path,
                rel=CampaignReport.LinkPurpose.SCENARIO_REPORT,
            ))  # type: Xml.Node

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
                # Don't set the testcase/failure/@message attribute in other cases.
                # That would just result in duplicating the error text with the node content generated below.
                pass

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
            # Don't duplicate the information if testcase/link[@rel='log'] already given, with a local file.
            if not (
                test_case_execution.log.path
                and test_case_execution.log.path.is_file()
                and test_case_execution.log.path.is_relative_to(self._report_path.parent)
            ):
                _xml_system_out = _xml_test_case.appendchild(xml_doc.createnode("system-out"))  # type: Xml.Node
                _xml_system_out.appendchild(xml_doc.createtextnode(self._safestr2xml(test_case_execution.log.content.decode("utf-8"))))

        # testcase/system-err:
        # [CUBIC]: "Data that was written to standard error while the test was executed. optional"
        # Due to `CampaignRunner` implementation, stderr will be given as a testcase/failure node.

        return _xml_test_case

    def _xml2testcase(
            self,
            test_suite_execution,  # type: _TestSuiteExecutionType
            xml_test_case,  # type: _XmlType.Node
    ):  # type: (...) -> _TestCaseExecutionType
        """
        Test case reading from JUnit XML.

        :param test_suite_execution: Owner test suite execution instance.
        :param xml_test_case: JUnit XML to read from.
        :return: Test case execution data.
        """
        from ._campaignexecution import TestCaseExecution
        from ._executionstatus import ExecutionStatus
        from ._knownissues import KnownIssue
        from ._testerrors import ExceptionError, TestError
        from ._xmlutils import Xml

        # Note: The testcase/@name attribute is filled with the pretty path.
        #       The testcase/@classname attribute gives the full path.
        # _name = xml_test_case.getattr("name")  # type: str
        _script_path = self._xmlattr2path(xml_test_case, "classname")  # type: _PathType
        self.debug("testcase/@classname = '%s'", _script_path)

        _test_case_execution = TestCaseExecution(test_suite_execution, _script_path)  # type: TestCaseExecution

        if xml_test_case.hasattr("time"):
            _test_case_execution.time.elapsed = float(xml_test_case.getattr("time"))
            self.debug("testcase/@time = %f", _test_case_execution.time.elapsed)

        for _xml_link in xml_test_case.getchildren("link"):  # type: Xml.Node
            _link_purpose = _xml_link.getattr("rel")  # type: str
            if _link_purpose == CampaignReport.LinkPurpose.SCENARIO_LOG:
                _test_case_execution.log.path = self._xmlattr2path(_xml_link, "href")
                self.debug("testcase/link[@rel=%r]/@href = '%s'", _link_purpose, _test_case_execution.log.path)
                if self._read_scenario_logs:
                    # Read the log file by the way.
                    self.debug("Reading scenario log from '%s'", _test_case_execution.log.path)
                    _test_case_execution.log.read()  # Let exceptions raise up.
            elif _link_purpose == CampaignReport.LinkPurpose.SCENARIO_REPORT:
                _test_case_execution.report.path = self._xmlattr2path(_xml_link, "href")
                self.debug("testcase/link[@rel=%r]/@href = '%s'", _link_purpose, _test_case_execution.report.path)
                if self._read_scenario_reports:
                    # Read the scenario report by the way.
                    self.debug("Reading scenario report from '%s'", _test_case_execution.report.path)
                    _test_case_execution.report.read()  # Let exceptions raise up.
            else:
                self.warning(f"Unknown testcase/link/@rel value {_link_purpose!r}")

        # Failures have already been filled by reading the scenario report above.
        # Let's reset them, and build them again (at the scenario level only), this time from the JUnit report information.
        if _test_case_execution.scenario_execution:
            _test_case_execution.scenario_execution.errors = []
            for _xml_failure in xml_test_case.getchildren("failure"):  # type: Xml.Node
                self.debug("New testcase/failure")
                if _xml_failure.hasattr("message") and (_test_case_execution.scenario_execution is not None):
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
                            _error.location = _FAST_PATH.code_location.fromlongstring(":".join(_last_line.split(":")[:3]))
                            self.debug("testcase/failure/@location = '%s'", _error.location.tolongstring())
                    _test_case_execution.scenario_execution.errors.append(_error)
        if xml_test_case.hasattr("status"):
            _status = xml_test_case.getattr("status")  # type: str
            self.debug("testcase/@status = %r", _status)
            # Don't check testcase/@status v/s errors when the scenario report has not been read.
            if _test_case_execution.report.content is not None:
                if _test_case_execution.errors and (_status != str(ExecutionStatus.FAIL)):
                    self.warning(f"{_test_case_execution.name}: Mismatching status {_status!r} with {len(_test_case_execution.errors)} error count")
                if (not _test_case_execution.errors) and (_status == str(ExecutionStatus.FAIL)):
                    self.warning(f"{_test_case_execution.name}: Mismatching status {_status!r} while no error")

        if _test_case_execution.scenario_execution:
            # Check the `scenario` statistics, which are properties of `TestCase`.
            self._xmlcheckstats(_test_case_execution.name, xml_test_case, [_test_case_execution.scenario_execution])

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
        from ._logformatter import LogFormatter

        return LogFormatter.nocolor(string)

    def _path2xmlattr(
            self,
            xml_node,  # type: _XmlType.Node
            attr_name,  # type: str
            path,  # type: _PathType
    ):  # type: (...) -> None
        """
        Sets a path XML attribute.

        Sets either a relative or absolute path
        depending on the given file location compared with this JUnit file location.

        :param xml_node: XML node to set the attribute for.
        :param attr_name: Attribute name.
        :param path: Path object to use to set the attribute value.
        """
        xml_node.setattr(attr_name, path.relative_to(self._report_path.parent))

    def _xmlattr2path(
            self,
            xml_node,  # type: _XmlType.Node
            attr_name,  # type: str
    ):  # type: (...) -> _PathType
        """
        Path computation from an XML attribute.

        When the attribute describes a relative path, the path is computed from the JUnit file.
        When it describes an absolute path, the path is taken as is.

        :param xml_node: XML node which attribute to read from.
        :param attr_name: Attribute name to read.
        :return: Path computed.
        """
        return _PathImpl(xml_node.getattr(attr_name), relative_to=self._report_path.parent)

    def _path2xmllink(
            self,
            xml_doc,  # type: _XmlType.Document
            path,  # type: _PathType
            rel,  # type: CampaignReport.LinkPurpose
    ):  # type: (...) -> _XmlType.Node
        """
        Creates a ``<link/>`` item.

        Non JUnit standard.
        Syntax inspired from HTML ``<link rel="stylesheet" type="text/css" href=""/>`` items.

        :param xml_doc: XML document to create the new node with.
        :param path: Path of the document to link.
        :param rel: Purpose of the document.
        :return: New ``<link/>`` node created.
        """
        from ._jsondictutils import JsonDict

        _xml_link = xml_doc.createnode("link")  # type: _XmlType.Node

        # Path of the file.
        self._path2xmlattr(_xml_link, "href", path)

        # Purpose of the file.
        _xml_link.setattr("rel", rel)

        # Set content type depending on file suffix.
        if path.suffix.lower() in [".log"]:
            _xml_link.setattr("type", "text/plain")
        elif JsonDict.isjson(path):
            _xml_link.setattr("type", "application/json")
        elif JsonDict.isyaml(path):
            _xml_link.setattr("type", "application/yaml")
        else:
            raise ValueError(f"Unknwon content type '{path}'")

        return _xml_link

    def _objectstats2xmlattr(
            self,
            xml_node,  # type: _XmlType.Node
            stat_object,  # type: _StatObjectType
    ):  # type: (...) -> None
        """
        Creates `scenario` statistics attributes.

        Non JUnit standard...

        :param xml_node: XML node to set attributes for.
        :param stat_object: Object to read statistics from.
        """
        for _stat_name in CampaignReport.StatAttrName:  # type: CampaignReport.StatAttrName
            xml_node.setattr(_stat_name, str(CampaignReport._getobjectstat(stat_object, _stat_name)))

    def _xmlcheckstats(
            self,
            node_name,  # type: str
            xml_node,  # type: _XmlType.Node
            stat_subobjects,  # type: typing.Sequence[_StatObjectType]
    ):  # type: (...) -> None
        """
        Statistics consistency checking between an upper level and its children.

        :param node_name: Name of the object corresponding to ``xml_node``.
        :param xml_node: Upper XML node which statistics to check.
        :param stat_subobjects: Subobjects to check statistics with.

        Displays warnings when the statistics mismatch.
        """
        # Don't check statistics if scenario reports have not been read.
        if not self._read_scenario_reports:
            return

        class _StatResult:
            def __init__(self, stat_name):  # type: (CampaignReport.StatAttrName) -> None
                self.stat_name = stat_name  # type: CampaignReport.StatAttrName
                self.match = False  # type: bool
                self.top_count = 0  # type: int
                self.sum_count = 0  # type: int

                if xml_node.hasattr(self.stat_name):
                    self.top_count = int(xml_node.getattr(self.stat_name))
                    self.sum_count = sum([CampaignReport._getobjectstat(_stat_subobject, self.stat_name) for _stat_subobject in stat_subobjects])
                    self.match = (self.top_count == self.sum_count)
        _stats = [
            _StatResult(_stat_name)  # noqa  ## Bad IDE type checking on `_stat_attr_name`
            for _stat_name in CampaignReport.StatAttrName
        ]  # type: typing.Sequence[_StatResult]
        if not all(map(lambda res: res.match, _stats)):
            _errors = ", ".join(map(
                lambda res: f"{res.stat_name}: {res.top_count} != {res.sum_count}",
                filter(lambda res: not res.match, _stats),
            ))  # type: str
            self.warning(f"{node_name}: Mismatching statistics ({_errors})")

    @staticmethod
    def _getobjectstat(
            stat_object,  # type: _StatObjectType
            stat_name,  # type: CampaignReport.StatAttrName
    ):  # type: (...) -> int
        """
        Retrieves the expected statistic from a given object.

        :param stat_object: Object to read statistics from.
        :param stat_name: Statistic name to read.
        :return: Statistic read from ``stat_object``.
        """
        from ._campaignexecution import CampaignExecution, TestCaseExecution, TestSuiteExecution
        from ._scenarioexecution import ScenarioExecution

        assert stat_name.count("-") == 1, f"Bad stat name {stat_name!r}"
        _stat_type, _exec_total = stat_name.split("-")  # type: str, str
        if isinstance(stat_object, ScenarioExecution):
            return int(getattr(getattr(stat_object, _stat_type[:-1] + "_stats"), _exec_total))
        elif isinstance(stat_object, (CampaignExecution, TestSuiteExecution, TestCaseExecution)):
            return int(getattr(getattr(stat_object, _stat_type), _exec_total))
        else:
            raise TypeError(f"Unhandled object type {stat_object!r}")


#: Main instance of :class:`CampaignReport`.
CAMPAIGN_REPORT = CampaignReport()  # type: CampaignReport
