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

import re
import typing

import scenario
import scenario.test

from . import paths


class TestData:

    def __init__(
            self,
            path,  # type: scenario.Path
            expected_locations,  # type: typing.Dict[str, str]
    ):
        self.path = path  # type: scenario.Path
        #: Dictionary of {location key: code location}
        self.locations = {}  # type: typing.Dict[str, scenario.CodeLocation]

        self.__const_name = ""  # type: str

        scenario.logging.info("")
        scenario.logging.info("Processing '%s':" % path)

        self._findlocations(expected_locations)

    @property
    def const_name(self):  # type: (...) -> str
        if not self.__const_name:
            # Search for the test data constant name in the `scenario.test.paths` module.
            _vars = vars(scenario.test.paths)  # type: typing.Dict[str, typing.Any]
            for _var_name in _vars:  # type: str
                _var = _vars[_var_name]  # type: typing.Any
                if isinstance(_var, scenario.Path):
                    if _var.samefile(self.path):
                        scenario.logging.debug("'%s' => '%s'", self.path, _var_name)
                        self.__const_name = _var_name
                        break
        assert self.__const_name, "Could not retrieve path constant name for '%s" % self.path
        return self.__const_name

    def _findlocations(
            self,
            expected_locations,  # type: typing.Dict[str, str]
    ):  # type: (...) -> None
        """
        Find and save code locations

        :param expected_locations: Dictionary of {location key: function name} to find out.
        """
        # Will be dequeued, make a copy.
        expected_locations = expected_locations.copy()

        # Read the source file line by line and find out test data locations.
        _line_number = 0  # type: int
        for _line in self.path.read_bytes().splitlines():  # type: bytes
            _line_number += 1
            _match = re.match(rb'^.* {2}# location: (.*)$', _line)  # type: typing.Optional[typing.Match[bytes]]
            if _match:
                _key = _match.group(1).decode("utf-8")  # type: str
                assert _key in expected_locations, "%s: Unknown key '%s' in line %d" % (self.path, _key, _line_number)
                _function = expected_locations.pop(_key)  # type: str
                self.locations[_key] = scenario.CodeLocation(self.path, _line_number, _function)

        # Check all expected locations have been found.
        assert not expected_locations, "%s: Location keys not found: %s" % (self.path, ", ".join(expected_locations.keys()))


class FileUpdater:

    def __init__(
            self,
            path,  # type: scenario.Path
            test_data,  # type: TestData
            *match_modify_line_handlers,  # type: MatchModifyHandlerType
    ):  # type: (...) -> None
        self.path = path  # type: scenario.Path
        self.test_data = test_data  # type: TestData

        self.__output_lines = []  # type: typing.List[bytes]
        self.__match_modify_line_handlers = list(match_modify_line_handlers)  # type: typing.List[MatchModifyHandlerType]

    def launch(self):  # type: (...) -> None
        # Reset output lines.
        self.__output_lines = []

        # Process the file line by line.
        for _line in self.path.read_bytes().splitlines():  # type: bytes
            scenario.logging.debug("%s:%d: %r", self.path, self._current_line, _line)

            # Call each match/modify handler one by one, until one of them returned a modified line.
            _new_line = None  # type: typing.Optional[bytes]
            for _match_modify_line_handler in self.__match_modify_line_handlers:  # type: MatchModifyHandlerType
                _new_line = _match_modify_line_handler(self, _line)
                if _new_line is not None:
                    break

            # Log and store the (un)modified line.
            if (_new_line is not None) and (_new_line != _line):
                scenario.logging.warning("  %s:%d: << %r" % (self.path, self._current_line, _line.strip()))
                scenario.logging.warning("  %s:%d: >> %r" % (self.path, self._current_line, _new_line.strip()))
            elif _new_line is not None:
                scenario.logging.info("  %s:%d: (unchanged) %r" % (self.path, self._current_line, _new_line.strip()))
            else:
                # Keep the line as is by default.
                _new_line = _line
            self.__output_lines.append(_new_line)

        # Ensure/restore a final empty line.
        self.__output_lines.append(b'')

        # Dump the file with fixed locations.
        self._writefile()

    @property
    def _current_line(self):  # type: (...) -> int
        return len(self.__output_lines) + 1

    def matchmodifyline(
            self,
            regex,  # type: bytes
            line,  # type: bytes
            filter_match,  # type: typing.Optional[typing.Callable[[typing.Match[bytes]], bool]]
            location_key,  # type: typing.Callable[[typing.Match[bytes]], str]
            new_line,  # type: typing.Callable[[typing.Match[bytes], scenario.CodeLocation], bytes]
    ):  # type: (...) -> typing.Optional[bytes]
        _match = re.match(regex, line)  # type: typing.Optional[typing.Match[bytes]]
        if _match:
            # Apply match filtering.
            if filter_match is not None:
                if not filter_match(_match):
                    scenario.logging.debug("Match with %r filtered out" % regex)
                    return None

            # Determine the location key.
            _key = location_key(_match)  # type: str
            assert _key in self.test_data.locations, "%s:%d: No such location key '%s' in '%s'" % (self.path, self._current_line, _key, self.test_data.path)

            # Compute and return the modified line.
            return new_line(_match, self.test_data.locations[_key])
        elif self.test_data.path.prettypath.encode("utf-8") in line:
            scenario.logging.debug("Regex %r did not match" % regex)

        return None

    def _writefile(self):  # type: (...) -> None
        self.path.write_bytes(b'\n'.join(self.__output_lines))


if typing.TYPE_CHECKING:
    MatchModifyHandlerType = typing.Callable[[FileUpdater, bytes], typing.Optional[bytes]]


def updatefile(
        path,  # type: scenario.Path
        test_data,  # type: TestData
        *match_modify_line_handlers,  # type: MatchModifyHandlerType
):  # type: (...) -> None
    FileUpdater(path, test_data, *match_modify_line_handlers).launch()


class DataExpectationsUpdater(FileUpdater):
    """
    Dedicated to scenario expectations in the `scenario.test.data` module.
    """

    def __init__(
            self,
            test_data,  # type: TestData
    ):  # type: (...) -> None
        FileUpdater.__init__(
            self,
            paths.TEST_SRC_DATA_PATH, test_data,
            lambda _, line: self.matchmodifyline(
                rb'^(.*location=.*:)\d+(:.*, {2}# location: (.*)/(.*))$', line,
                filter_match=lambda match: self._filtermatch(match, 3),
                location_key=lambda match: match.group(4).decode("utf-8"),
                new_line=lambda match, location: b'%s%d%s' % (match.group(1), location.line, match.group(2)),
            )
        )

    def _filtermatch(
            self,
            match,  # type: typing.Match[bytes]
            test_data_const_name_groupe_index,  # type: int
    ):  # type: (...) -> bool
        _test_data_const_name = match.group(test_data_const_name_groupe_index).decode("utf-8")  # type: str
        if _test_data_const_name != self.test_data.const_name:
            scenario.logging.debug("Data path constant name mismatch %r != %r", _test_data_const_name, self.test_data.const_name)
            return False
        return True


def updatedataexpectations(
        test_data,  # type: TestData
):  # type: (...) -> None
    DataExpectationsUpdater(test_data).launch()


class KeyListFileUpdater(FileUpdater):
    """
    Useful for log and JSON files.
    """

    def __init__(
            self,
            path,  # type: scenario.Path
            test_data,  # type: TestData
            ordered_location_keys,  # type: typing.List[str]
            regex,  # type: bytes
            pretty_path,  # type: typing.Callable[[typing.Match[bytes]], str]
            new_line,  # type: typing.Callable[[typing.Match[bytes], scenario.CodeLocation], bytes]
    ):  # type: (...) -> None
        """
        Update locations in a log file.

        :param path: File path to update.
        :param test_data: Test data.
        :param ordered_location_keys: List of ordered location keys to use along the file. Must match the number of locations to update in the log file.
        :param regex: Regular expression to use to match lines.
        :param pretty_path: Location pretty path extractor handler.
        :param new_line: New line builder handler.
        """
        FileUpdater.__init__(
            self,
            path, test_data,
            lambda _, line: self.matchmodifyline(
                regex, line,
                # Fix lines corresponding to the input test data file only.
                filter_match=lambda match: pretty_path(match) == self.test_data.path.prettypath,
                # Pop the next location key in queue.
                location_key=lambda match: self._nextlocationkey(),
                new_line=new_line,
            ),
        )

        # Will be dequeued, make a copy.
        self._ordered_location_keys = ordered_location_keys.copy()  # type: typing.List[str]

    def _nextlocationkey(self):  # type: (...) -> str
        assert self._ordered_location_keys, "%s: Not enough location keys" % self.path
        return self._ordered_location_keys.pop(0)

    def _writefile(self):  # type: (...) -> None
        # Check all expected JSON lines have been processed prior to writing the file.
        assert not self._ordered_location_keys, "%s: Unprocessed keys: %s" % (self.path, ", ".join(self._ordered_location_keys))
        # Call the method of the parent class when the assertion succeeded.
        super()._writefile()


def updatelog(
        path,  # type: scenario.Path
        test_data,  # type: TestData
        ordered_location_keys,  # type: typing.List[str]
):  # type: (...) -> None
    KeyListFileUpdater(
        path, test_data, ordered_location_keys,
        rb'^(.*\((.*):)\d+(:.*\))$',
        pretty_path=lambda match: match.group(2).decode("utf-8"),
        new_line=lambda match, location: b'%s%d%s' % (match.group(1), location.line, match.group(3)),
    ).launch()


def updatejson(
        path,  # type: scenario.Path
        test_data,  # type: TestData
        ordered_location_keys,  # type: typing.List[str]
):  # type: (...) -> None
    # JsonFileUpdater(path, test_data, ordered_location_keys).launch()
    KeyListFileUpdater(
        path, test_data, ordered_location_keys,
        rb'^( *"location": "(.*):)\d+(:.*(",|"))$',
        pretty_path=lambda match: match.group(2).decode("utf-8"),
        new_line=lambda match, location: b'%s%d%s' % (match.group(1), location.line, match.group(3)),
    ).launch()
