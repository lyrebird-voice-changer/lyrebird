#!/usr/bin/env bash
set -eu -o pipefail

[ ! -e /etc/redhat-release ] && echo Only Redhat releases are supported && exit 1

# change PWD to repo root
cd "$(dirname "$0")/.."

INTERACTIVE_ARG="--assumeyes"
[[ $- == *i* ]] && INTERACTIVE_ARG=""
SUDO_CMD="sudo"
[[ $(id --user) == 0 ]] && SUDO_CMD=""
$SUDO_CMD dnf install "$INTERACTIVE_ARG" dnf-plugins-core rpm-build rpmdevtools

rpmdev-setuptree
spectool --get-files --directory "${HOME}/rpmbuild/SOURCES" lyrebird.spec
$SUDO_CMD dnf builddep --assumeyes --spec lyrebird.spec
rpmbuild -bb lyrebird.spec

find "${HOME}/rpmbuild/RPMS" -name '*.rpm' -exec cp "{}" ./ci  \;
