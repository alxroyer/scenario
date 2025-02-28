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
 * @brief Expandable/collapsible lists.
 */


/** @var {object} `scenario.lists` package. */
scenario.lists = {};


// Add 'click' event listeners to `a.expand-all.list` and `a.collapse-all.list` buttons.
scenario.onLoad(() => {
    /**
     * @brief Configures `.expand-all` and `.collapse-all` buttons.
     * @param {"expand-all" | "collapse-all"} buttonClass Button class.
     * @param {"expanded" | "collapsed"} newState Final state wanted.
     * @returns {void}
     */
    function _configButton(buttonClass, newState) {
        for (/** @var {HTMLElement} */ const _button of scenario.findNodes(document.body, `a.button.${buttonClass}.list`)) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                /** @var {string | null} */ const _listCid = scenario.getCid(_button, "list");
                if (_listCid) {
                    scenario.lists._toggleAll(_listCid, newState);
                }
            });
        }
    }
    _configButton("expand-all", "expanded");
    _configButton("collapse-all", "collapsed");
});


/**
 * @brief Expands or collapses all list items.
 * @param {string} listCid List CID.
 * @param {"expanded" | "collapsed"} newState Final state wanted.
 * @returns {void}
 */
scenario.lists._toggleAll = (listCid, newState) => {
    console.debug(`scenario.lists._toggleAll('${listCid}', '${newState}')`);

    /** @var {number} */ let _count = 0;

    // Find the list corresponding to the given CID.
    for (/** @var {HTMLElement} */ const _list of scenario.findNodes(document.body, `ul.list=${listCid}`)) {
        // Don't call `scenario.lists._toggle()` directly,
        // but `scenario.divs.toggle()` that will call `scenario.lists.checkToggleLi1()` to have `scenario.lists._toggle()` possibly called in the end.

        // Use `scenario.divs.findAndToggleAll()` to process all list items,
        // and make it recursive on items' contents by the way.
        scenario.divs.findAndToggleAll(_list, newState, {
            // Use the `buttonProcessed()` callback to count `.li1` main items processed.
            /**
             * @param {HTMLElement} button `.toggle-div` button processed.
             * @returns {void}
             */
            buttonProcessed: (button) => {
                if (scenario.nodeMatches(button, `a.toggle-li1.list=${listCid}`)) {
                    _count ++;
                }
            },
        });
    }

    console.debug(`scenario.lists._toggleAll('${listCid}', '${newState}'): ${_count} \`.li1\` main item(s) ${newState}`);
};


/**
 * @brief Check whether the given `button`, just toggled, corresponds to a `.li1` main item, and should call `scenario.lists._toggle()` complementary actions.
 * @param {HTMLElement} button Button just toggled by `scenario.divs.toggle()`.
 * @param {"expanded" | "collapsed"} newState Final state wanted.
 * @returns {void}
 *
 * Called by `scenario.divs.toggle()`.
 */
scenario.lists.checkToggleLi1 = (button, newState) => {
    // Check whether the given button owns a `.li1` main item CID.
    /** @var {string | null} */ const _li1Cid = scenario.getCid(button, "li1");
    if (_li1Cid) {
        // If so, find the ancestor `.li1` main item.
        for (/** @var {HTMLElement | undefined} */ let _parent = button.parentNode; _parent; _parent = _parent.parentNode) {
            if (scenario.nodeMatches(_parent, `li.li1=${_li1Cid}`)) {
                // Call `scenario.lists._toggle()` complementary actions.
                scenario.lists._toggle(_parent, {
                    li1Cid: _li1Cid,
                    //oldState: ...,  // Let `scenario.lists._toggle()` read actual li1's current state.
                    newState: newState,
                });

                // `.li1` main item found and processed. Stop iterating.
                break;
            }
        }
    }
};


/**
 * @brief Finishes expanding or collapsing a `.li1` main item (`scenario.divs.toggle()` complement).
 * @param {HTMLElement} li1 Main item to expand or collapse.
 * @param {string | null | undefined} li1Cid CID of main item, if already known (performance concerns).
 * @param {"expanded" | "collapsed" | null | undefined} oldState Current state, if already known (performance concerns).
 * @param {"expanded" | "collapsed" | null | undefined} newState Final state wanted. Switch state if not provided.
 * @returns {void}
 *
 * Called by `scenario.lists.checkToggleLi1()`.
 */
scenario.lists._toggle = (li1, {li1Cid, oldState, newState} = {}) => {
    // Read CID from classes.
    if (li1Cid === undefined) {
        li1Cid = scenario.getCid(li1, "li1");
    }

    // Determine old state from classes if not provided.
    if (oldState === undefined) {
        oldState = scenario.findOneClassOf(li1, ["expanded", "collapsed"]);
    }

    // Compute `newState` if not provided.
    if (! newState) {
        // Reverse status.
        switch (oldState) {
            case "expanded": newState = "collapsed"; break;
            case "collapsed": newState = "expanded"; break;
        }
    }

    if (li1Cid && oldState && newState) {
        console.debug(`Toggling li1 ${li1Cid}: ${oldState} => ${newState}`);

        // Remove old state and set new state on `.li1` main item.
        li1.classList.remove("expanded");
        li1.classList.remove("collapsed");
        li1.classList.add(newState);

        // Hide/show `.li1` comments sum-up.
        if (scenario.nodeMatches(li1, `li.li1.li1=${li1Cid}.comments-sum-up`)) {
            for (/** @var {HTMLElement} */ const _span of scenario.findNodes(li1, `span.li1.li1=${li1Cid}`)) {
                if (scenario.nodeMatches(_span, ".sep") || scenario.nodeMatches(_span, ".comment")) {
                    switch (newState) {
                        case "expanded": _span.style.display = "none"; break;
                        case "collapsed": _span.style.display = "inline-block"; break;
                    }
                }
            }
        }
    }
};
