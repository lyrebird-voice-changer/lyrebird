#!/bin/sh

DIR="$(dirname $0)"
cd "$DIR/../share/lyrebird"
exec python3 app.py
