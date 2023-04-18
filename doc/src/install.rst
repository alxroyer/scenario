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


.. _install:

Installation
============

Prerequisites
-------------

Mandatory:

- Python 3.6 or later (https://www.python.org/downloads/)

  - Python >= 3.7 recommended (for compatibility with mypy v1.0.0).
  - Tested with versions 3.6.8 and 3.7.9.

Recommended:

- mypy (https://pypi.org/project/mypy/)

  - Versions prior to 1.0.0 not supported anymore.
  - Tested with version 1.0.1 (Python 3.7.9).

- pytz (https://pypi.org/project/pytz/)

- PyYAML (https://pypi.org/project/PyYAML/)

Documentation generation (optional):

- Sphinx (https://pypi.org/project/Sphinx/)

  - Tested with version 4.4.0 (Python 3.6.8) and 5.3.0 (Python 3.7.9, version used on readthedocs as of 2023-04-13).

- readthedocs:

  - Memo of the readthedocs command

    .. code-block:: bash

        $ python -m pip install --upgrade --no-cache-dir \
          pillow \
          mock==1.0.1 \
          alabaster>=0.7,<0.8,!=0.7.5 \
          commonmark==0.9.1 \
          recommonmark==0.5.0 \
          sphinx \
          sphinx-rtd-theme \
          readthedocs-sphinx-ext<2.3

        Collecting pillow
          Downloading Pillow-9.5.0-cp37-cp37m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.3 MB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.3/3.3 MB 172.3 MB/s eta 0:00:00
        Collecting mock==1.0.1
          Downloading mock-1.0.1.zip (861 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 861.9/861.9 kB 213.8 MB/s eta 0:00:00
          Preparing metadata (setup.py): started
          Preparing metadata (setup.py): finished with status 'done'
        Collecting alabaster!=0.7.5,<0.8,>=0.7
          Downloading alabaster-0.7.13-py3-none-any.whl (13 kB)
        Collecting commonmark==0.9.1
          Downloading commonmark-0.9.1-py2.py3-none-any.whl (51 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 51.1/51.1 kB 178.3 MB/s eta 0:00:00
        Collecting recommonmark==0.5.0
          Downloading recommonmark-0.5.0-py2.py3-none-any.whl (9.8 kB)
        Collecting sphinx
          Downloading sphinx-5.3.0-py3-none-any.whl (3.2 MB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.2/3.2 MB 182.7 MB/s eta 0:00:00
        Collecting sphinx-rtd-theme
          Downloading sphinx_rtd_theme-1.2.0-py2.py3-none-any.whl (2.8 MB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.8/2.8 MB 182.5 MB/s eta 0:00:00
        Collecting readthedocs-sphinx-ext<2.3
          Downloading readthedocs_sphinx_ext-2.2.0-py2.py3-none-any.whl (11 kB)
        Collecting docutils>=0.11
          Downloading docutils-0.19-py3-none-any.whl (570 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 570.5/570.5 kB 215.4 MB/s eta 0:00:00
        Collecting packaging>=21.0
          Downloading packaging-23.1-py3-none-any.whl (48 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.9/48.9 kB 179.6 MB/s eta 0:00:00
        Collecting sphinxcontrib-devhelp
          Downloading sphinxcontrib_devhelp-1.0.2-py2.py3-none-any.whl (84 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 84.7/84.7 kB 128.3 MB/s eta 0:00:00
        Collecting imagesize>=1.3
          Downloading imagesize-1.4.1-py2.py3-none-any.whl (8.8 kB)
        Collecting importlib-metadata>=4.8
          Downloading importlib_metadata-6.3.0-py3-none-any.whl (22 kB)
        Collecting babel>=2.9
          Downloading Babel-2.12.1-py3-none-any.whl (10.1 MB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.1/10.1 MB 167.3 MB/s eta 0:00:00
        Collecting sphinxcontrib-applehelp
          Downloading sphinxcontrib_applehelp-1.0.2-py2.py3-none-any.whl (121 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 121.2/121.2 kB 207.6 MB/s eta 0:00:00
        Collecting sphinxcontrib-jsmath
          Downloading sphinxcontrib_jsmath-1.0.1-py2.py3-none-any.whl (5.1 kB)
        Collecting Jinja2>=3.0
          Downloading Jinja2-3.1.2-py3-none-any.whl (133 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 133.1/133.1 kB 209.9 MB/s eta 0:00:00
        Collecting sphinxcontrib-serializinghtml>=1.1.5
          Downloading sphinxcontrib_serializinghtml-1.1.5-py2.py3-none-any.whl (94 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 94.0/94.0 kB 211.0 MB/s eta 0:00:00
        Collecting Pygments>=2.12
          Downloading Pygments-2.15.0-py3-none-any.whl (1.1 MB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 187.3 MB/s eta 0:00:00
        Collecting sphinxcontrib-htmlhelp>=2.0.0
          Downloading sphinxcontrib_htmlhelp-2.0.0-py2.py3-none-any.whl (100 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.5/100.5 kB 208.5 MB/s eta 0:00:00
        Collecting snowballstemmer>=2.0
          Downloading snowballstemmer-2.2.0-py2.py3-none-any.whl (93 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 93.0/93.0 kB 182.4 MB/s eta 0:00:00
        Collecting requests>=2.5.0
          Downloading requests-2.28.2-py3-none-any.whl (62 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.8/62.8 kB 192.0 MB/s eta 0:00:00
        Collecting sphinxcontrib-qthelp
          Downloading sphinxcontrib_qthelp-1.0.3-py2.py3-none-any.whl (90 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90.6/90.6 kB 217.6 MB/s eta 0:00:00
        Collecting sphinxcontrib-jquery!=3.0.0,>=2.0.0
          Downloading sphinxcontrib_jquery-4.1-py2.py3-none-any.whl (121 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 121.1/121.1 kB 222.9 MB/s eta 0:00:00
        Collecting docutils>=0.11
          Downloading docutils-0.18.1-py2.py3-none-any.whl (570 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 570.0/570.0 kB 210.0 MB/s eta 0:00:00
        Collecting pytz>=2015.7
          Downloading pytz-2023.3-py2.py3-none-any.whl (502 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 502.3/502.3 kB 212.7 MB/s eta 0:00:00
        Collecting zipp>=0.5
          Downloading zipp-3.15.0-py3-none-any.whl (6.8 kB)
        Collecting typing-extensions>=3.6.4
          Downloading typing_extensions-4.5.0-py3-none-any.whl (27 kB)
        Collecting MarkupSafe>=2.0
          Downloading MarkupSafe-2.1.2-cp37-cp37m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (25 kB)
        Collecting idna<4,>=2.5
          Downloading idna-3.4-py3-none-any.whl (61 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 61.5/61.5 kB 182.7 MB/s eta 0:00:00
        Collecting certifi>=2017.4.17
          Downloading certifi-2022.12.7-py3-none-any.whl (155 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 155.3/155.3 kB 221.8 MB/s eta 0:00:00
        Collecting charset-normalizer<4,>=2
          Downloading charset_normalizer-3.1.0-cp37-cp37m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (171 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 171.0/171.0 kB 225.9 MB/s eta 0:00:00
        Collecting urllib3<1.27,>=1.21.1
          Downloading urllib3-1.26.15-py2.py3-none-any.whl (140 kB)
             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 140.9/140.9 kB 224.3 MB/s eta 0:00:00
        Building wheels for collected packages: mock
          Building wheel for mock (setup.py): started
          Building wheel for mock (setup.py): finished with status 'done'
          Created wheel for mock: filename=mock-1.0.1-py3-none-any.whl size=23772 sha256=9732711d1f6085fefc55ab2f0a037c2579d36ad65d00f13881becee259b45a4d
          Stored in directory: /tmp/pip-ephem-wheel-cache-zvv9_sp8/wheels/7a/94/b1/0fdc5339a5bd487a5cc15421ec200d9ba3e2aa7190e4a727f1
        Successfully built mock
        Installing collected packages: snowballstemmer, pytz, mock, commonmark, zipp, urllib3, typing-extensions, sphinxcontrib-serializinghtml, sphinxcontrib-qthelp, sphinxcontrib-jsmath, sphinxcontrib-htmlhelp, sphinxcontrib-devhelp, sphinxcontrib-applehelp, Pygments, pillow, packaging, MarkupSafe, imagesize, idna, docutils, charset-normalizer, certifi, babel, alabaster, requests, Jinja2, importlib-metadata, sphinx, readthedocs-sphinx-ext, sphinxcontrib-jquery, recommonmark, sphinx-rtd-theme
        Successfully installed Jinja2-3.1.2 MarkupSafe-2.1.2 Pygments-2.15.0 alabaster-0.7.13 babel-2.12.1 certifi-2022.12.7 charset-normalizer-3.1.0 commonmark-0.9.1 docutils-0.18.1 idna-3.4 imagesize-1.4.1 importlib-metadata-6.3.0 mock-1.0.1 packaging-23.1 pillow-9.5.0 pytz-2023.3 readthedocs-sphinx-ext-2.2.0 recommonmark-0.5.0 requests-2.28.2 snowballstemmer-2.2.0 sphinx-5.3.0 sphinx-rtd-theme-1.2.0 sphinxcontrib-applehelp-1.0.2 sphinxcontrib-devhelp-1.0.2 sphinxcontrib-htmlhelp-2.0.0 sphinxcontrib-jquery-4.1 sphinxcontrib-jsmath-1.0.1 sphinxcontrib-qthelp-1.0.3 sphinxcontrib-serializinghtml-1.1.5 typing-extensions-4.5.0 urllib3-1.26.15 zipp-3.15.0

  - ``pip install sphinx-rtd-theme``
  - ``pip install "readthedocs-sphinx-ext<2.3"``
  - ``pip install "mock==1.0.1"``
  - ``pip install "commonmark==0.9.1"``
  - ``pip install "recommonmark==0.5.0"``
  - ``pip install pillow``
  - in 'scenario/': ``python -m sphinx -T -E -b html -D language=en ./tools/conf/sphinx/ ./doc/html/``
    or ``./sphinx-rtd.sh 2>&1 > sphinx-rtd.log``

- Java

  - Tested with version 11.0.14.


From sources
------------

Clone the project sources:

.. code-block:: bash

    $ git clone https://github.com/alxroyer/scenario

Use the 'bin/run-test.py' or 'bin/run-campaign.py' launchers directly.
Let's say you had cloned the project in '/path/to/scenario':

.. code-block:: bash

    $ /path/to/scenario/bin/run-test.py --help
    $ /path/to/scenario/bin/run-campaign.py --help
