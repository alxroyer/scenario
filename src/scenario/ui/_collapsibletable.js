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
 * @brief Expandable/collapsible tables.
 */


/** @var {object} `scenario.tables` package. */
scenario.tables = {};


// Add 'click' event listeners to `a.expand-all` and `a.collapse-all` buttons.
scenario.onLoad(() => {
    /**
     * @brief Configures `.expand-all` and `.collapse-all` buttons.
     * @param {"expand-all" | "collapse-all"} buttonClass Button class.
     * @param {"expanded" | "collapsed"} newState Final state wanted.
     * @returns {void}
     */
    function _configButton(buttonClass, newState) {
        for (/** @var {HTMLElement} */ const _button of scenario.findNodes(document.body, `a.button.${buttonClass}`)) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                /** @var {string | null} */ const _tableId = scenario.getNamedObjectIdFromClasses(_button, "table");
                if (_tableId) {
                    scenario.tables._toggleAll(_tableId, newState);
                }
            });
        }
    }
    _configButton("expand-all", "expanded");
    _configButton("collapse-all", "collapsed");
});


// Add 'click' event listeners on `a.toggle-row` buttons.
scenario.onLoad(() => {
    for (/** @var {HTMLElement} */ const _mainRow of scenario.findNodes(document.body, "table.collapsible tr.main-row")) {
        for (/** @var {HTMLElement} */ const _button of scenario.findNodes(_mainRow, "a.button.toggle-row")) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                scenario.tables._toggle(_mainRow);
            });
        }
    }
});


/**
 * @brief Expands or collapses all main rows.
 * @param {string} tableId Table identifier.
 * @param {"expanded" | "collapsed"} newState Final state wanted.
 * @returns {void}
 */
scenario.tables._toggleAll = (tableId, newState) => {
    console.debug(`scenario.tables._toggleAll('${tableId}', '${newState}')`);
    /** @var {number} */ let _count = 0;
    for (/** @var {HTMLElement} */ const _mainRow of scenario.findNodes(document.body, `table.collapsible.table=${tableId} tr.main-row`)) {
        scenario.tables._toggle(_mainRow, {newState: newState, collapsibleListItems: true});
        _count ++;
    }
    console.debug(`scenario.tables._toggleAll('${tableId}', '${newState}'): ${_count} main row(s) ${newState}`);
};


/**
 * @brief Expands or collapses `.collapsible-row` rows attached to a given `.main-row` row.
 * @param {HTMLElement} mainRow Main row to expand or collapse.
 * @param {"expanded" | "collapsed" | undefined} newState Final state wanted. Switch state if not provided.
 * @param {boolean | undefined} collapsibleListItems `true` to apply `newState` to related collapsible list items. Lists unchanged by default.
 * @returns {void}
 */
scenario.tables._toggle = (mainRow, {newState, collapsibleListItems} = {}) => {
    // Find 'main-row=...' id and 'expanded'/'collapsed' state from classes.
    /** @var {string | null} */ const _mainRowId = scenario.getNamedObjectIdFromClasses(mainRow, "main-row");
    if (! _mainRowId) {
        console.error(`No main row identifier found from ${mainRow} classes`);
        return;
    }
    /** @var {string | null} */ const _oldState = (
        mainRow.classList.contains("expanded") ? "expanded" :
        mainRow.classList.contains("collapsed") ? "collapsed" :
        null  // Neither 'expanded' nor 'collapsed'.
    );

    // Compute `newState` if not provided.
    if (! newState) {
        // Reverse status.
        switch (_oldState) {
            case "expanded": newState = "collapsed"; break;
            case "collapsed": newState = "expanded"; break;
        }
    }

    // Toggle from `_oldState` to `newState`.
    /** @var {HTMLElement | null} */ const _table = mainRow.parentElement;
    if (_table && _mainRowId && _oldState && newState) {
        console.debug(`Toggling ${_mainRowId}: ${_oldState} => ${newState}`);

        for (/** @var {HTMLElement} */ const _tr of scenario.findNodes(_table, `tr.main-row=${_mainRowId}`)) {
            // Remove old state.
            _tr.classList.remove("expanded");
            _tr.classList.remove("collapsed");

            // Set new state.
            _tr.classList.add(newState);

            // Adjust `tr.main-row a.button.toggle-row span` button text.
            if (_tr.classList.contains("main-row")) {
                for (/** @var {HTMLElement} */ const _buttonSpan of scenario.findNodes(_tr, "a.button.toggle-row span")) {
                    switch (newState) {
                        case "expanded": _buttonSpan.innerText = "-"; break;
                        case "collapsed": _buttonSpan.innerText = "+"; break;
                    }
                }
            }

            // Hide / show `tr.collapsible-row` rows.
            if (_tr.classList.contains("collapsible-row")) {
                switch (newState) {
                    case "expanded": _tr.style.visibility = "visible"; break;
                    case "collapsed": _tr.style.visibility = "collapse"; break;
                }
            }
        }
    }

    // Expand/collapse collapsible list items when required.
    if (collapsibleListItems && _table && _mainRowId) {
        for (/** @var {HTMLElement} */ const _tr of scenario.findNodes(_table, `tr.main-row=${_mainRowId}`)) {
            for (/** @var {HTMLElement} */ const _mainLi of scenario.findNodes(_tr, "li.collapsible.main-list-item")) {
                scenario.lists.toggle(_mainLi, {newState: newState});
            }
        }
    }
};
