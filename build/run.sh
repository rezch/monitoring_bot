#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT="$SCRIPT_DIR"/..
BOTENV="$ROOT"/botenv

if ! [ -d "$BOTENV" ]; then
  echo "bot env: $BOTENV doesn't exist."
  echo "installing env..."
  source "$SCRIPT_DIR"/install.sh
fi

source "$BOTENV"/bin/activate

TOKEN=$(grep -v '^#' "$ROOT"/.env | grep -m1 'TELEGRAM_API_TOKEN')

if [[ -z "$TOKEN" ]]; then
  echo 'Bot token not found. Please specify token in .env file.'
else
  echo "Starting bot..."
  export "$TOKEN"
  python3.11 -B "$ROOT"/source/main.py
fi
