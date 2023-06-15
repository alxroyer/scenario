.. Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..     http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _coding-rules.git:

Git strategy
============


.. _coding-rules.git.commit-messages:

Commit messages
---------------

Use common git message format guidelines, such as:

- `<https://www.freecodecamp.org/news/writing-good-commit-messages-a-practical-guide/>`_
- `<https://chris.beams.io/posts/git-commit/>`_

Special commit messages defined with :ref:`delivery guidelines <coding-rules.git.deliver>`.


.. _coding-rules.git.branches:

Branching strategy
------------------

.. todo:: Documentation needed: Describe the branching strategy.

    - Possibly *git-flow* once we have tested it? Not sure...
    - branch names:

      - Development branches:

        - feature/#xxx/detailed-description
        - bugfix/#xxx/detailed-description
        - hotfix/#xxx/detailed-description
        - enhancement/#xxx/detail-description
        - documentation/#xxx/detailed-description

      - Integration branches:

        - int/vX.Y.Z+
        - merge/int/vX.Y.Z+/vA.B.C

      - Reference branches:

        - master


.. _coding-rules.git.deliver:

Deliver with squash merge
^^^^^^^^^^^^^^^^^^^^^^^^^

.. todo:: Document squash merge deliveries.

    - ``git merge --ff-only --squash``
    - In order to be able to clean up development and integration branches when they are no more useful.
    - Commit message shall be summed up (complying with :ref:`commit message conventions <coding-rules.git.commit-messages>`).
    - Issue references shall be mentionned.
    - ``git tag vA.B.C`` when delivering a reference version.
    - Then on the source branch, a backward merge shall be done (in order to save track of the delivery operation):

      - with branch:

        - Same branch when delivering a development branch
          (this merge closes the development branch).
        - *merge/int/vX.Y.Z+/vA.B.C* when delivering the *int/vX.Y.Z+* integration branch as a *vA.B.C* reference version
          (in order 1) not to alter version numbers on the integration, so that 2) the latter can still be continued).

      - commit messages:

        - "Delivered into 'int/vX.Y.Z+'" for development branches delivered into an integration branch.
        - "Delivered as vX.Y.Z" for integration branches delivered as a reference version.
