#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "$SCRIPT_DIR"/source_env.sh

echo "Checking for whitespaces..."
"$BOTENV"/bin/pylint --disable=all --enable=C0303 $(find "$ROOT"/source -name '*.py')
