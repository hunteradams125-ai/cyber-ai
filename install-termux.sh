#!/data/data/com.termux/files/usr/bin/bash
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  if command -v pkg >/dev/null 2>&1; then
    pkg update -y
    pkg install -y python
  else
    echo "Python is required. Install Python in Termux and run this script again." >&2
    exit 1
  fi
fi

if command -v pkg >/dev/null 2>&1; then
  # These are optional tools. The application still runs when any are absent.
  pkg install -y openssl || true
fi

cd "$ROOT_DIR"
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt

mkdir -p "${CYBER_AI_HOME:-$HOME/.cyber-ai}"/{evidence,logs}
echo "CYBER AI is installed. Start it with: python cyber_ai.py"