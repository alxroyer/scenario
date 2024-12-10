/*
 * Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


/**
 * @file
 * @brief Campaign list page Javascript.
 */


/** @var {object} `scenario.campaigns` package. */
scenario.campaigns = {};


// Add 'click' event listeners to `a#expand-all` and `a#collapse-all` buttons.
scenario.onLoad(() => {
    /** @var {HTMLElement?} */ const _campaignsDiv = document.getElementById("campaigns");
    if (_campaignsDiv) {
        /** @var {HTMLElement?} */ const _expandAllButton = document.getElementById("expand-all");
        if (_expandAllButton) {
            _expandAllButton.addEventListener("click", (e) => {
                e.preventDefault();

                scenario.campaigns._toggleAllSuites("expanded");
            });
        }
        /** @var {HTMLElement?} */ const _collapseAllButton = document.getElementById("collapse-all");
        if (_collapseAllButton) {
            _collapseAllButton.addEventListener("click", (e) => {
                e.preventDefault();

                scenario.campaigns._toggleAllSuites("collapsed");
            });
        }
    }
});

// Add 'click' event listeners on `div#campaigns tr.suite` buttons.
scenario.onLoad(() => {
    /** @var {HTMLElement?} */ const _campaignsDiv = document.getElementById("campaigns");
    if (_campaignsDiv) {
        for (/** @var {HTMLElement} */ const _tr of _campaignsDiv.getElementsByTagName("tr")) {
            for (/** @var {HTMLElement} */ const _button of _tr.getElementsByClassName("button")) {
                _button.addEventListener("click", (e) => {
                    e.preventDefault();

                    scenario.campaigns._toggleSuite(_tr, undefined);
                });
            }
        }
    }
});


/**
 * @brief Expands or collapses all test suites.
 * @param {"expanded"|"collapsed"} newState Final state wanted.
 * @returns {void}
 */
scenario.campaigns._toggleAllSuites = (newState) => {
    /** @var {HTMLElement?} */ const _campaignsDiv = document.getElementById("campaigns");
    if (_campaignsDiv) {
        console.debug(`scenario.campaigns._allSuites('${newState}')`);
        /** @var {number} */ let _count = 0;
        for (/** @var {HTMLElement} */ const _tr of _campaignsDiv.getElementsByTagName("tr")) {
            if (_tr.classList.contains("suite")) {
                scenario.campaigns._toggleSuite(_tr, newState);
                _count ++;
            }
        }
        console.debug(`scenario.campaigns._allSuites('${newState}'): ${_count} suite(s) ${newState}`);
    }
};


/**
 * @brief Expands or collapses test cases of a given test suite.
 * @param {HTMLElement} tr `<tr class="suite"></tr>` to expand or collapse.
 * @param {"expanded"|"collapsed"|undefined} newState Final state wanted. Switch state if not provided.
 * @returns {void}
 */
scenario.campaigns._toggleSuite = (tr, newState) => {
    // Find 'suite=...' id and 'expanded'/'collapsed' state from classes.
    /** @var {string?} */ let _suiteNameClass = undefined;
    /** @var {string?} */ let _oldState = undefined;
    for (/** @var {string} */ const _class of tr.classList) {
        switch (_class) {
            case "expanded":
            case "collapsed":
                _oldState = _class;
                break;
            default:
                if (_class.startsWith("suite=")) {
                    _suiteNameClass = _class;
                }
                break;
        }
    }
    if (! _suiteNameClass) {
        console.error(`No suite name found from ${tr} classes`);
        return;
    }
    if (! _oldState) {
        // Consider 'expanded' by default.
        _oldState = "expanded";
    }

    // Compute `newState` if not provided.
    if (! newState) {
        // Reverse status.
        switch (_oldState) {
            case "expanded": newState = "collapsed"; break;
            case "collapsed": newState = "expanded"; break;
        }
    }

    console.debug(`Toggling ${_suiteNameClass}: ${_oldState} => ${newState}`);
    /** @var {HTMLElement?} */ const _table = tr.parentElement;
    if (_table && _suiteNameClass && newState) {
        for (/** @var {HTMLElement} */ const _tr of _table.getElementsByClassName(_suiteNameClass)) {
            // Remove old state, if any.
            _tr.classList.remove("expanded");
            _tr.classList.remove("collapsed");

            // Set new state.
            _tr.classList.add(newState);

            // Adjust `tr.suite a.button span` button text.
            if (_tr.classList.contains("suite")) {
                for (/** @var {HTMLElement} */ const _button of _tr.getElementsByClassName("button")) {
                    for (/** @var {HTMLElement} */ const _buttonSpan of _button.getElementsByTagName("span")) {
                        switch (newState) {
                            case "expanded": _buttonSpan.innerText = "-"; break;
                            case "collapsed": _buttonSpan.innerText = "+"; break;
                        }
                    }
                }
            }

            // Hide / show `tr.case` rows.
            if (_tr.classList.contains("case")) {
                switch (newState) {
                    case "expanded": _tr.style.visibility = "visible"; break;
                    case "collapsed": _tr.style.visibility = "collapse"; break;
                }
            }
        }
    }
};
