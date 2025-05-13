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
 * @brief Expandable/collapsible divs.
 */


/** @var {object} `scenario.divs` package. */
scenario.divs = {};


// Add 'click' event listeners on `a.toggle-div` buttons.
scenario.onLoad(() => {
    for (/** @var {HTMLElement} */ const _button of scenario.findNodes(document.body, "a.button.toggle-div")) {
        _button.addEventListener("click", (e) => {
            e.preventDefault();

            scenario.divs.toggle(_button);
        });
    }
});


/**
 * @brief Finds all collapsible divs in `focus` and applies `newState` on each.
 * @param {HTMLElement} focus Node which collapsible divs should be searched in.
 * @param {"expanded" | "collapsed"} newState New state to apply.
 * @param {((HTMLElement) => void) | undefined} buttonProcessed Callback for each `.toggle-div` button processed.
 * @returns {void}
 */
scenario.divs.findAndToggleAll = (focus, newState, {buttonProcessed} = {}) => {
    for (/** @var {HTMLElement} */ const _button of scenario.findNodes(focus, "a.button.toggle-div")) {
        // Process the `.toggle-div` button.
        scenario.divs.toggle(_button, {
            container: focus,  // Performance: restrict to `focus` at least.
            newState: newState,
        });

        // Call the `buttonProcessed()` callback if provided.
        if (buttonProcessed) {
            buttonProcessed(_button);
        }
    }
};


/**
 * @brief Shows or hides the `div.collapsible` attached with the given toggle button.
 * @param {HTMLElement} button Toggle button.
 * @param {string | null | undefined} divCid CID of the div to show/hide. Optional. Read from button classes if not provided.
 * @param {HTMLElement | null | undefined} container Container node for button and collapsible div. May be given, if known, for performance concerns.
 * @param {"expanded" | "collapsed" | undefined} newState Final state wanted. Switch state if not provided.
 * @returns {void}
 *
 * Calls `scenario.lists.checkToggleLi1()` on `button` (in case `button` stands for a `.li1` main list item).
 */
scenario.divs.toggle = (button, {divCid, container, newState} = {}) => {
    // Read CID from classes.
    if (! divCid) {
        divCid = scenario.getCid(button, "div");
    }

    // Ensure a candidate value for `container`.
    container = container || button.parentNode;

    // Find the collapsible div(s).
    /** @var {HTMLElement[]} */ const _collapsibleDivs = [];
    if (divCid) {
        /** @var {string} */ const _collapsibleDivSelector = `div.collapsible.div=${divCid}`;
        // Try from `container` first.
        if (container) {
            _collapsibleDivs.push(...scenario.findNodes(container, _collapsibleDivSelector));
        }
        // If not found try from `document.body`.
        if (! _collapsibleDivs.length) {
            _collapsibleDivs.push(...scenario.findNodes(document.body, _collapsibleDivSelector));
        }
    }

    // Determine old state from classes.
    /** @var {string | null} */ const _oldState = scenario.findOneClassOf(button, ["expanded", "collapsed"]);

    // Compute `newState` if not provided.
    if (! newState) {
        // Reverse status.
        switch (_oldState) {
            case "expanded": newState = "collapsed"; break;
            case "collapsed": newState = "expanded"; break;
        }
    }

    if (divCid && _collapsibleDivs.length && _oldState && newState) {
        console.debug(`Toggling div ${divCid}: ${_oldState} => ${newState}`);

        // Toggle button.
        scenario.buttons.setCollapsibleState(button, newState);

        // Collapsible div(s).
        for (/** @var {HTMLElement} */ const _collapsibleDiv of _collapsibleDivs) {
            // Remove old state and set new state on collapsible div.
            _collapsibleDiv.classList.remove("expanded");
            _collapsibleDiv.classList.remove("collapsed");
            _collapsibleDiv.classList.add(newState);

            // Adjust collapsible div visibility.
            switch (newState) {
                case "expanded": _collapsibleDiv.style.display = "block"; break;
                case "collapsed": _collapsibleDiv.style.display = "none"; break;
            }
        }

        // `.li` complementary actions.
        scenario.lists.checkToggleLi1(button, newState);
    }
};
