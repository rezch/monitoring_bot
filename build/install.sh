#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BOTENV=$SCRIPT_DIR/"../botenv"

PY_LIBS=(
  "psutil"
  "pyyaml"
)

if ! type python3.11; then
    echo "installing python3.11"
    sudo apt install -y python3.11
    sudo apt install -y python3.11-pip
    python3.11 -m ensurepip --user --upgrade
    python3.11 -m pip install --upgrade pip
    sudo apt install -y python3.11-venv
fi

# ------------ INSTALL VENV ------------

if ! [ -d "$BOTENV" ]; then
    echo "starting installing env"
    sudo python3.11 -m venv $BOTENV
    sudo chmod -R 777 $BOTENV
fi

echo "source env"
source $BOTENV/bin/activate

# ------------ INSTALL PY LIBS ------------

for lib in "${PY_LIBS[@]}"; do
  if ! python3.11 -m pip list | grep $lib; then
    yes | python3.11 -m pip install $lib
  fi
done
