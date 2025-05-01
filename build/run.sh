#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "$SCRIPT_DIR"/source_env.sh

TOKEN=$(grep -v '^#' "$ROOT"/.env | grep -m1 'TELEGRAM_API_TOKEN')

if [[ -z "$TOKEN" ]]; then
  echo 'Bot token not found. Please specify token in .env file.'
  exit 1
fi

echo "Starting bot..."
export "$TOKEN"
python3.11 -B "$ROOT"/source/main.py
