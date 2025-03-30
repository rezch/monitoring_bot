#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BOTENV=$SCRIPT_DIR/"../botenv"

if ! [ -d "$BOTENV" ]; then
  echo "bot env: $BOTENV doesn't exist."
  echo "installing env..."
  source $SCRIPT_DIR/install.sh
fi

source $BOTENV/bin/activate

if [[ -z "$TOKEN" ]]; then
  echo 'Bot token not found. Please specify token, by "export $TOKEN=<your_token>".'
else
  echo "Starting bot..."
  python3.11 source/main.py
fi
