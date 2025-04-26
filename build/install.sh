#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BOTENV="$SCRIPT_DIR"/../botenv

if ! [[ type python3.11]]; then
    echo "installing python3.11"

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update

    sudo apt install -y python3.11
    sudo apt install -y python3.11-pip
    python3.11 -m ensurepip --user --upgrade
    python3.11 -m pip install --upgrade pip
    sudo apt install -y python3.11-venv
fi

# ------------ INSTALL VENV ------------

if ! [[ -d "$BOTENV" ]]; then
    echo "starting installing env"
    sudo python3.11 -m venv $BOTENV
    sudo chmod -R 777 $BOTENV
fi

echo "source env"
source "$BOTENV"/bin/activate
source "$BOTENV"/bin/activate

# ------------ INSTALL PY LIBS ------------

pip install -r "$SCRIPT_DIR"/requirements.txt
