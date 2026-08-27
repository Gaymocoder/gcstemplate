#!/usr/bin/env sh

GCST_WERROR="${GCST_WERROR:-OFF}"
export GCST_WERROR

python3 .gcst/scripts/build.py "$@"