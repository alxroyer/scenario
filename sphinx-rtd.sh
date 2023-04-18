#!/usr/bin/env bash

rm -rf ./doc/html/
python -m sphinx -T -E -b html -D language=en ./tools/conf/sphinx/ ./doc/html/
rm -rf ./doc/json/
