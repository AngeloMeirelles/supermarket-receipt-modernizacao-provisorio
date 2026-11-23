"""Gera as evidências de testes, qualidade e segurança do projeto.

Uso, a partir da pasta do projeto:
    python scripts/gerar_evidencias.py antes
    python scripts/gerar_evidencias.py depois

Os testes rodam no ambiente do projeto (venv) e as ferramentas de análise
rodam em um ambiente separado (venv-ferramentas), para que o pip-audit e o
Safety auditem apenas as dependências do projeto.
"""

import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = "Scripts" if sys.platform == "win32" else "bin"
PROJECT_BIN = ROOT / "venv" / BIN_DIR
TOOLS_BIN = ROOT / "venv-ferramentas" / BIN_DIR
PHASES = ("antes", "depois")
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def execute(command: list[str], timeout: int = 600) -> tuple[str, str]:
    """Executa um comando e devolve o código de saída e a saída sem cores."""
    env = {
        **os.environ,
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "NO_COLOR": "1",
    }
    try:
        result = subprocess.run(
            command,
            check=False,
            cwd=ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"tempo limite de {timeout}s excedido", ""
    output = ANSI_ESCAPE.sub("", result.stdout + result.stderr).strip()
    return str(result.returncode), output


def section(command: list[str]) -> str:
    """Monta o trecho do registro: comando, data, código de saída e saída."""
    started_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exit_code, output = execute(command)
    shown_command = " ".join([Path(command[0]).name, *command[1:]])
    return f"$ {shown_command}\n# executado em {started_at} | código de saída: {exit_code}\n\n{output}\n"


def save(folder: Path, file_name: str, commands: list[list[str]]) -> None:
    (folder / file_name).write_text(
        "\n\n".join(section(c) for c in commands), encoding="utf-8"
    )
    print(f"  {file_name}")


def tool(name: str) -> str:
    return str(TOOLS_BIN / name)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
        sys.exit(f"Uso: python scripts/gerar_evidencias.py {{{'|'.join(PHASES)}}}")

    folder = ROOT / "docs" / "evidencias" / sys.argv[1]
    folder.mkdir(parents=True, exist_ok=True)
    python = str(PROJECT_BIN / "python")

    # Versões exatas instaladas no ambiente do projeto: é este o escopo auditado.
    frozen_requirements = folder / "dependencias_instaladas.txt"
    _, installed = execute([python, "-m", "pip", "freeze"])
    frozen_requirements.write_text(installed + "\n", encoding="utf-8")
    audited_file = frozen_requirements.relative_to(ROOT).as_posix()

    print(f"Gerando evidências em {folder.relative_to(ROOT).as_posix()}")
    save(
        folder,
        "00_ambiente.txt",
        [
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            ["git", "log", "-1", "--format=%H %s"],
            [python, "--version"],
            [python, "-c", "import platform; print(platform.platform())"],
            [tool("ruff"), "--version"],
            [tool("mypy"), "--version"],
            [tool("radon"), "--version"],
            [tool("bandit"), "--version"],
            [tool("pip-audit"), "--version"],
            [tool("safety"), "--version"],
        ],
    )
    save(folder, "01_pytest.txt", [[python, "-m", "pytest", "-v"]])
    save(
        folder,
        "02_cobertura.txt",
        [
            [python, "-m", "coverage", "run", "--source=src", "-m", "pytest", "-q"],
            [python, "-m", "coverage", "report", "-m"],
        ],
    )
    save(
        folder,
        "03_ruff.txt",
        [
            [tool("ruff"), "check", "src", "tests"],
            [tool("ruff"), "format", "--check", "src", "tests"],
        ],
    )
    save(
        folder,
        "04_mypy.txt",
        [
            [tool("mypy"), "src"],
            [tool("mypy"), "--strict", "src"],
        ],
    )
    save(
        folder,
        "05_radon.txt",
        [
            [tool("radon"), "cc", "src", "-s", "-a"],
            [tool("radon"), "mi", "src", "-s"],
        ],
    )
    save(folder, "06_bandit.txt", [[tool("bandit"), "-r", "src"]])
    save(
        folder,
        "07_pip_audit.txt",
        [[tool("pip-audit"), "-r", audited_file, "--no-deps"]],
    )
    save(
        folder,
        "08_safety.txt",
        [
            [tool("safety"), "check", "-r", audited_file],
            [tool("safety"), "scan", "--target", "."],
        ],
    )


if __name__ == "__main__":
    main()
