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


// Add 'click' event listeners to `a.expand-all.table` and `a.collapse-all.table` buttons.
scenario.onLoad(() => {
    /**
     * @brief Configures `.expand-all` and `.collapse-all` buttons.
     * @param {"expand-all" | "collapse-all"} buttonClass Button class.
     * @param {"expanded" | "collapsed"} newState Final state wanted.
     * @returns {void}
     */
    function _configButton(buttonClass, newState) {
        for (/** @var {HTMLElement} */ const _button of scenario.findNodes(document.body, `a.button.${buttonClass}.table`)) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                /** @var {string | null} */ const _tableCid = scenario.getCid(_button, "table");
                if (_tableCid) {
                    scenario.tables._toggleAll(_tableCid, newState);
                }
            });
        }
    }
    _configButton("expand-all", "expanded");
    _configButton("collapse-all", "collapsed");
});


// Add 'click' event listeners on `a.toggle-tr1` buttons.
scenario.onLoad(() => {
    for (/** @var {HTMLElement} */ const _tr1 of scenario.findNodes(document.body, "table tr.tr1.collapsible")) {
        for (/** @var {HTMLElement} */ const _button of scenario.findNodes(_tr1, "a.button.toggle-tr1")) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                scenario.tables._toggle(_tr1);
            });
        }
    }
});


/**
 * @brief Expands or collapses all main rows.
 * @param {string} tableCid Table CID.
 * @param {"expanded" | "collapsed"} newState Final state wanted.
 * @returns {void}
 */
scenario.tables._toggleAll = (tableCid, newState) => {
    console.debug(`scenario.tables._toggleAll('${tableCid}', '${newState}')`);

    /** @var {number} */ let _count = 0;

    for (/** @var {HTMLElement} */ const _tr1 of scenario.findNodes(document.body, `tr.tr1.table=${tableCid}`)) {
        scenario.tables._toggle(_tr1, {newState: newState, recursive: true});
        _count ++;
    }

    console.debug(`scenario.tables._toggleAll('${tableCid}', '${newState}'): ${_count} main row(s) ${newState}`);
};


/**
 * @brief Expands or collapses a `.tr1` main row.
 * @param {HTMLElement} tr1 Main row to expand or collapse.
 * @param {"expanded" | "collapsed" | undefined} newState Final state wanted. Switch state if not provided.
 * @param {boolean | undefined} recursive `true` to apply `newState` to collapsible divs and list items contained in the row. Items unchanged by default.
 * @returns {void}
 */
scenario.tables._toggle = (tr1, {newState, recursive} = {}) => {
    // Read CID from classes.
    /** @var {string | null} */ const _tr1Cid = scenario.getCid(tr1, "tr1");
    if (! _tr1Cid) {
        console.error(`No tr1 CID found from ${tr1} classes`);
        return;
    }

    // Determine old state from classes.
    /** @var {string | null} */ const _oldState = scenario.findOneClassOf(tr1, ["expanded", "collapsed"]);

    // Compute `newState` if not provided.
    if (! newState) {
        // Reverse status.
        switch (_oldState) {
            case "expanded": newState = "collapsed"; break;
            case "collapsed": newState = "expanded"; break;
        }
    }

    /** @var {HTMLElement | null} */ const _table = tr1.parentElement;
    if (_table && _tr1Cid && (_oldState || recursive) && newState) {
        if (_oldState) {
            console.debug(`Toggling tr1 ${_tr1Cid}: ${_oldState} => ${newState}`);
        }

        // Walk `.tr1` and `.tr2` rows corresponding to the given tr1 CID.
        for (/** @var {HTMLElement} */ const _tr of scenario.findNodes(_table, `tr.tr1=${_tr1Cid}`)) {
            // Toggle from `_oldState` to `newState`.
            if (_oldState) {
                // Remove old state and set new state on the row.
                _tr.classList.remove("expanded");
                _tr.classList.remove("collapsed");
                _tr.classList.add(newState);

                // Toggle button.
                if (scenario.nodeMatches(_tr, "tr.tr1")) {
                    for (/** @var {HTMLElement} */ const _button of scenario.findNodes(_tr, "a.button.toggle-tr1")) {
                        scenario.buttons.setCollapsibleState(_button, newState);
                    }
                }

                // Hide / show `tr.tr2` rows.
                if (scenario.nodeMatches(_tr, "tr.tr2")) {
                    switch (newState) {
                        case "expanded": _tr.style.visibility = "visible"; break;
                        case "collapsed": _tr.style.visibility = "collapse"; break;
                    }
                }
            }

            // Recursively expand/collapse items when required.
            if (recursive) {
                scenario.divs.findAndToggleAll(_tr, newState);
            }
        }
    }
};


/**
 * @brief Ensures the given `.tr1` main row is expanded if `node` is in a related `.tr2` subrow.
 * @param {HTMLElement} node Node to check whether in a related `.tr2` subrow.
 * @returns {void}
 */
scenario.tables.ensureExpanded = (node) => {
    // Get back to the nearest `.tr2` ancestor node.
    for (/** @var {HTMLElement} */ const _tr2 of scenario.findNodes(node, "tr.tr2", {axis: "ancestors", limit: 1})) {
        // Read the `tr1` CID.
        /** @var {string | null} */ const _tr1Cid = scenario.getCid(_tr2, "tr1");
        if (_tr1Cid) {
            // Get back to the `table` ancestor node.
            for (/** @var {HTMLElement} */ const _table of scenario.findNodes(_tr2, "table", {axis: "ancestors", limit: 1})) {
                // Find the related `.tr1` main row.
                for (/** @var {HTMLElement} */ const _tr1 of scenario.findNodes(_table, `tr.tr1.tr1=${_tr1Cid}`)) {
                    // Ensure the `.tr1` main row is expanded.
                    scenario.tables._toggle(_tr1, {newState: "expanded"});
                }
            }
        }
    }
};
