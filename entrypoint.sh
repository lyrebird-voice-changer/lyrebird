#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null && pwd )"

cd "${DIR}/../share/lyrebird"
exec python3 app.py
