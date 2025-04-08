#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SOURCE="$SCRIPT_DIR/../source"

find $SOURCE -type d -name "__pycache__" -exec rm -rv {} \;
