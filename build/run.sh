#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$SCRIPT_DIR/..
BOTENV=$ROOT/botenv

if ! [ -d "$BOTENV" ]; then
  echo "bot env: $BOTENV doesn't exist."
  echo "installing env..."
  source $SCRIPT_DIR/install.sh
fi

source $BOTENV/bin/activate

export $(grep -m1 'TELEGRAM_API_TOKEN' $ROOT/.env)

if [[ -z "$TELEGRAM_API_TOKEN" ]]; then
  echo 'Bot token not found. Please specify token in .env file.'
else
  echo "Starting bot..."
  python3.11 -B source/main.py
fi
