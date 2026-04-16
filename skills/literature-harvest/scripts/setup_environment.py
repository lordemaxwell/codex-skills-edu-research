from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def venv_python(skill_dir: Path) -> Path:
    if os.name == "nt":
        return skill_dir / ".venv" / "Scripts" / "python.exe"
    return skill_dir / ".venv" / "bin" / "python"


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent
    requirements = skill_dir / "requirements.txt"
    venv_dir = skill_dir / ".venv"

    if not venv_dir.exists():
        print("Creating virtual environment...")
        result = subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        if result.returncode != 0:
            return result.returncode

    python_path = venv_python(skill_dir)
    print("Installing Python dependencies...")
    result = subprocess.run([str(python_path), "-m", "pip", "install", "-r", str(requirements)])
    if result.returncode != 0:
        return result.returncode

    print("Installing Chromium for Playwright...")
    result = subprocess.run([str(python_path), "-m", "playwright", "install", "chromium"])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
