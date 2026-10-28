"""Check the active Python environment, PyMuPDF, and the local Ollama server."""
from __future__ import annotations

import argparse
import json
import platform
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from lab_common import ROOT, require_pymupdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="all-minilm:22m")
    parser.add_argument("--url", default="http://localhost:11434")
    parser.add_argument("--offline", action="store_true", help="Check PDF tools without contacting Ollama")
    args = parser.parse_args()
    print("OS:", platform.system(), platform.machine())
    print("Python:", platform.python_version())
    print("Interpreter:", sys.executable)
    print("Project root:", ROOT)
    if sys.version_info < (3, 10):
        raise SystemExit("Use Python 3.10 or newer; the workshop recommends 3.12-3.14.")
    print("Virtual environment:", "yes" if sys.prefix != sys.base_prefix else "NO - select .venv first")
    if sys.prefix == sys.base_prefix:
        raise SystemExit("Activate .venv or invoke its python executable directly.")
    module = require_pymupdf()
    print("PyMuPDF:", module.__version__)
    if args.offline:
        print("Ollama: skipped; PDF steps 03-07 are available offline.")
        return
    try:
        base = args.url.rstrip("/")
        with urlopen(base + "/api/version", timeout=10) as response:
            version = json.load(response)
        with urlopen(base + "/api/tags", timeout=10) as response:
            names = [item["name"] for item in json.load(response).get("models", [])]
    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"Ollama is not reachable at {args.url}: {exc}\nOpen Ollama app, or start its service. Do not start two servers.") from exc
    print("Ollama version:", version.get("version", "unknown"))
    print("Installed models:", ", ".join(names) or "none")
    if args.model not in names:
        raise SystemExit(f"Model missing: {args.model}\nRun: ollama pull {args.model}")
    print("Setup ready.")


if __name__ == "__main__":
    main()
