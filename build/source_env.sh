SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT="$SCRIPT_DIR"/..
BOTENV="$ROOT"/botenv

if ! [ -d "$BOTENV" ]; then
  echo "bot env: $BOTENV doesn't exist."
  echo "Installing env..."
  source "$SCRIPT_DIR"/install.sh
fi

source "$BOTENV"/bin/activate
