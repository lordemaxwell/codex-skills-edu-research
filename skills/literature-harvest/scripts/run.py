from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from common import load_local_env


SCRIPT_MAP = {
    "setup_environment": "setup_environment.py",
    "check_env": "check_env.py",
    "search_open": "search_open.py",
    "login_cnki": "login_cnki.py",
    "fetch_cnki": "fetch_cnki.py",
    "fetch_publisher": "fetch_publisher.py",
    "harvest_topic": "harvest_topic.py",
    "build_manifest": "build_manifest.py",
    "import_zotero": "import_zotero.py",
}


def candidate_pythons() -> list[Path]:
    env_python = os.environ.get("LIT_HARVEST_PYTHON")
    candidates = [
        env_python,
        sys.executable,
        r"D:\Python\Python311\python.exe",
        r"C:\Python311\python.exe",
    ]
    found: list[Path] = []
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists() and path not in found:
            found.append(path)
    return found


def get_venv_python(skill_dir: Path) -> Path:
    if os.name == "nt":
        return skill_dir / ".venv" / "Scripts" / "python.exe"
    return skill_dir / ".venv" / "bin" / "python"


def ensure_venv(skill_dir: Path) -> Path:
    venv_python = get_venv_python(skill_dir)
    if venv_python.exists():
        return venv_python

    system_python = candidate_pythons()
    if not system_python:
        raise RuntimeError("No usable system Python found. Set LIT_HARVEST_PYTHON.")

    setup_script = skill_dir / "scripts" / "setup_environment.py"
    result = subprocess.run([str(system_python[0]), str(setup_script)])
    if result.returncode != 0:
        raise RuntimeError("Failed to set up the virtual environment.")
    return venv_python


def main() -> int:
    load_local_env()
    if len(sys.argv) < 2:
        print("Usage: python run.py <command> [args...]")
        print("")
        print("Commands:")
        for command in SCRIPT_MAP:
            print(f"  {command}")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]
    script_name = SCRIPT_MAP.get(command, command)
    if not script_name.endswith(".py"):
        script_name = f"{script_name}.py"

    skill_dir = Path(__file__).resolve().parent.parent
    script_path = skill_dir / "scripts" / script_name
    if not script_path.exists():
        print(f"Script not found: {script_name}")
        return 1

    try:
        runner = ensure_venv(skill_dir)
    except Exception as exc:
        print(f"Environment error: {exc}")
        return 1

    result = subprocess.run([str(runner), str(script_path), *args])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
