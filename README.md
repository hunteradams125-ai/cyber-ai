# CYBER AI v1.0

CYBER AI is a phone-first cybersecurity learning, defensive monitoring,
evidence-analysis, and authorized-lab platform for Termux on Android.

Phase 1 provides the foundation:

- a modular Rich terminal interface
- SQLite structured storage
- explicit authorization records before target operations
- safe subprocess execution with argument arrays and no shell concatenation
- an evidence pipeline that hashes and stores raw collection output
- development fixtures for running without Android tools
- a credential-vault foundation using Fernet encryption

The project intentionally does not require root, Kali Linux, Docker, or
systemd. Android-specific collectors will be added behind adapters in later
phases.

## Run in development mode

```sh
cd cyber-ai
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
CYBER_AI_DEV_MODE=1 python cyber_ai.py
```

Run tests:

```sh
python -m unittest discover -s tests -v
```

## Termux

```sh
cd cyber-ai
chmod +x install-termux.sh
./install-termux.sh
python cyber_ai.py
```

Data is stored under `$CYBER_AI_HOME` when set, otherwise under
`~/.cyber-ai`. Raw evidence is kept separately from the SQLite database.

## Vault key

The vault never contains a hard-coded encryption key. Set
`CYBER_AI_VAULT_KEY` to a Fernet key before using the vault, or use a secure
secret manager outside this project. Never put the key in source control and
never print it in logs.