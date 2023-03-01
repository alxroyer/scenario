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


.. _guidelines:

Guidelines
==========

This section describes guidelines that shall be followed.

Bash commands are assumed to be executed from the root directory of the repository.


.. _guidelines.deliver:

Deliver on an integration branch
--------------------------------

1. Check licence headers:

   .. code-block:: bash

       repo-checklicenseheaders

   There should be no error.
   Fix headers if needed.
   If files have been modified, commit them (probably with the ``--amend`` option).

2. Check typings:

   .. code-block:: bash

       ./tools/checktypes.py

   There should be no error.
   Fix things if needed.
   If files have been modified, commit them (probably with the ``--amend`` option).

3. Check tests:

   Check test data is up-to-date:

   .. code-block:: bash

       ./tools/updatetestdata.py

   .. code-block:: bash

       ./test/run-unit-campaign.py

   There may be warnings, but no errors.

4. Check documentation:

   a. Generation the documentation:

      .. code-block:: bash

          rm -rf ./doc/html/
          ./tools/mkdoc.py

      Check the 'mkdoc.py' output log errors and warnings:

      - There may be TODO warnings, especially for sections that still have to be documented.
      - There may be warnings for "duplicate object" (see issue #25)

      There shall be no other errors.

   b. Check the HTML output in 'doc/html/':

      Check the pages that use the ``.. literalinclude::`` directive with the ``:lines:`` option
      (following list established on the 'int/v0.2.2+' branch):

      - advanced.config-db.html (depending on 'doc/data/run-demo.show-configs.log')
      - advanced.logging.html (depending on 'demo/loggingdemo.py', 3 times)

5. Check files encoding:

   Check all files use utf-8 encoding and unix end-of-line characters, and have the appropriate permissions:

   .. code-block:: bash

       repo-checkfiles --all

   If files have been modified, this should be minor modifications.
   Check line encoding modifications with ``git diff -b``.
   Commit the modifications (probably with the ``--amend`` option).


.. _guidelines.new-version:

Deliver a new version
---------------------

0. Merge on the master branch:

   .. code-block:: bash

       git checkout master
       git merge --squash --ff-only int/vX.Y.Z+

   Update the commit message, then:

   .. code-block:: bash

       git commit

1. Check the scenario version stored in the code:

   Check the version tuple defined in 'src/pkginfo.py'.

   If files have been modified, commit them (probably with the ``--amend`` option).

2. Apply :ref:`delivery checking <guidelines.deliver>` as described before.

3. Update the documentation:

   Check the ``copyright`` and ``version`` variables in 'tools/conf/sphinx/conf.py'.

   Regenerate the documentation:

   .. code-block:: bash

       rm -rf doc/html/
       ./tools/mkdoc.py

   Commit modifications (with the ``--amend`` option).

4. Add a tag on the final node:

   .. code-block:: bash

       git tag vX.Y.Z

5. Push on the github repository:

   .. code-block:: bash

       git push
       git push vX.Y.Z

6. Configure readthedocs:

   Go to the `readthedocs project page <https://readthedocs.org/projects/scenario-testing-framework/>`_.

   Configure a build for the new version, and set it as the default.
