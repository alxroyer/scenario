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


// Add 'click' event listeners on `a.toggle-list-item` buttons.
scenario.onLoad(() => {
    for (/** @var {HTMLElement} */ const _mainLi of scenario.findNodes(document.body, "li.collapsible.main-list-item")) {
        for (/** @var {HTMLElement} */ const _button of scenario.findNodes(_mainLi, "a.button.toggle-list-item")) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                scenario.lists.toggle(_mainLi);
            });
        }
    }
});


/**
 * @brief Expands or collapses `li.collapsible-list-item`s attached to a given `li.main-list-item`.
 * @param {HTMLElement} mainLi Main list item to expand or collapse.
 * @param {"expanded" | "collapsed" | undefined} newState Final state wanted. Switch state if not provided.
 * @returns {void}
 */
scenario.lists.toggle = (mainLi, {newState} = {}) => {
    // Find 'main-list-item=...' id and 'expanded'/'collapsed' state from classes.
    /** @var {string | null} */ const _mainListItemId = scenario.getNamedObjectIdFromClasses(mainLi, "main-list-item");
    if (! _mainListItemId) {
        console.error(`No main list item identifier found from ${mainLi} classes`);
        return;
    }
    /** @var {string | null} */ const _oldState = (
        mainLi.classList.contains("expanded") ? "expanded" :
        mainLi.classList.contains("collapsed") ? "collapsed" :
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

    if (_mainListItemId && _oldState && newState) {
        console.debug(`Toggling ${_mainListItemId}: ${_oldState} => ${newState}`);

        // Remove old state and set new state on main list item.
        mainLi.classList.remove("expanded");
        mainLi.classList.remove("collapsed");
        mainLi.classList.add(newState);

        // Adjust `a.button.toggle-list-item span` button text.
        for (/** @var {HTMLElement} */ const _buttonSpan of scenario.findNodes(mainLi, "a.button.toggle-list-item span")) {
            switch (newState) {
                case "expanded": _buttonSpan.innerText = "-"; break;
                case "collapsed": _buttonSpan.innerText = "+"; break;
            }
        }

        // Hide/show main list item comments sum-ups.
        if (mainLi.classList.contains("comments-sum-up")) {
            for (/** @var {HTMLElement} */ const _span of scenario.findNodes(mainLi, "span.main-list-item")) {
                if (_span.classList.contains("sep") || _span.classList.contains("comments")) {
                    switch (newState) {
                        case "expanded": _span.style.display = "none"; break;
                        case "collapsed": _span.style.display = "inline-block"; break;
                    }
                }
            }
        }

        // Walk `li.collapsible-list-item`s.
        for (/** @var {HTMLElement} */ const _collapsibleLi of scenario.findNodes(mainLi, `li.collapsible-list-item.main-list-item=${_mainListItemId}`)) {
            // Remove old state, and set new state.
            _collapsibleLi.classList.remove("expanded");
            _collapsibleLi.classList.remove("collapsed");
            _collapsibleLi.classList.add(newState);

            // Hide / show `tr.collapsible-row` rows.
            switch (newState) {
                case "expanded": _collapsibleLi.style.display = "block"; break;
                case "collapsed": _collapsibleLi.style.display = "none"; break;
            }
        }
    }
};
