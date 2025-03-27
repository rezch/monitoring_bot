#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BOTENV=$SCRIPT_DIR/"../botenv"

if ! type python3.10; then
    echo "installing python3.10"
    sudo apt install -y python3.10
fi

# ------------ INSTALL VENV ------------

if ! type python3-venv; then
    echo "installing python3-venv"
    sudo apt install -y python3-venv
fi

if ! [ -d "$BOTENV" ]; then
    echo "starting installing env"
    sudo python3 -m venv $BOTENV
    sudo chmod -R 777 $BOTENV
fi

echo "source env"
source $BOTENV/bin/activate

# ------------ INSTALL PY LIBS ------------

if ! type pip3; then
  echo "pip3 install"
  sudo apt install -y python3-pip
fi

if ! pip3 list | grep psutil; then
  yes | pip3 install psutil
fi
