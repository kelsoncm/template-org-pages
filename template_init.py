#!/usr/bin/env python3
"""Inicializa um repositório gerado a partir do template-org-pages.

Troca os marcadores ({{OWNER}}, {{TITLE}}, {{TAGLINE_EN}}, {{TAGLINE_PT}}...) do portal bilíngue e, por fim,
apaga este script.

Uso (na raiz do repositório recém-criado, ``<org>/<org>.github.io``):

    python template_init.py                       # pergunta o que não conseguir deduzir
    python template_init.py --title "Minha Suite" --tagline-en "..." --tagline-pt "..." --yes
    python template_init.py --dry-run             # mostra o que mudaria, sem alterar nada

Sem dependências externas: só a biblioteca padrão do Python 3.10+.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).resolve()
SKIP_DIRS = {".git", "node_modules", "vendor", ".venv", "venv", "__pycache__", "_build", "_site", "dist"}
TEMPLATE_BLOCK = re.compile(r"<!-- template:start -->.*?<!-- template:end -->\n*", re.S)
RST_UNDERLINE = re.compile(r"^([=\-~^\"'`#*+])\1+$")


def git(*args: str) -> str:
    """Executa um comando git na raiz e devolve a saída (vazia se o git falhar)."""
    try:
        result = subprocess.run(  # noqa: S603 - argumentos fixos, git do PATH do desenvolvedor
            ["git", *args],  # noqa: S607
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def remote_owner_repo() -> tuple[str, str]:
    """Deduz dono e nome do repositório pela URL do remoto ``origin``."""
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", git("remote", "get-url", "origin"))
    return (match.group(1), match.group(2)) if match else ("", "")


def ask(label: str, default: str, interactive: bool) -> str:
    """Pergunta um valor no terminal, usando o padrão quando não houver resposta."""
    if not interactive:
        return default
    answer = input(f"{label} [{default}]: ").strip() if default else input(f"{label}: ").strip()
    return answer or default


def iter_paths() -> list[Path]:
    """Lista arquivos e pastas do repositório, ignorando .git, dependências e saídas de build."""
    paths = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts) or path == SELF:
            continue
        paths.append(path)
    return paths


def fix_rst_underlines(text: str) -> str:
    """Ajusta o sublinhado dos títulos reStructuredText ao novo tamanho do título."""
    lines = text.split("\n")
    for i in range(1, len(lines)):
        title = lines[i - 1]
        if title.strip() and not RST_UNDERLINE.match(title) and RST_UNDERLINE.match(lines[i]):
            lines[i] = lines[i][0] * max(len(title), 3)
    return "\n".join(lines)


def apply(replacements: dict[str, str], dry_run: bool) -> None:
    """Troca os marcadores no conteúdo e nos nomes dos arquivos e pastas."""
    ordered = sorted(replacements.items(), key=lambda item: -len(item[0]))
    for path in iter_paths():
        if not path.is_file():
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            continue  # binário (imagens, fontes...)
        new = text
        for old, value in ordered:
            new = new.replace(old, value)
        new = TEMPLATE_BLOCK.sub("", new)
        if path.suffix == ".rst":
            new = fix_rst_underlines(new)
        if new != text:
            print(f"  editado:   {path.relative_to(ROOT).as_posix()}")
            if not dry_run:
                path.write_bytes(new.encode("utf-8"))
    for path in sorted(iter_paths(), key=lambda p: len(p.parts), reverse=True):
        name = path.name
        for old, value in ordered:
            name = name.replace(old, value)
        if name != path.name:
            print(f"  renomeado: {path.relative_to(ROOT).as_posix()} -> {name}")
            if not dry_run:
                path.rename(path.with_name(name))


def common_arguments(parser: argparse.ArgumentParser, owner: str) -> None:
    """Argumentos comuns a todos os templates."""
    parser.add_argument("--owner", default=owner, help="organização ou usuário do GitHub (padrão: remoto origin)")
    parser.add_argument("--author", default=git("config", "user.name"))
    parser.add_argument("--email", default=git("config", "user.email"))
    parser.add_argument("--yes", action="store_true", help="não pergunta nada; usa argumentos e padrões")
    parser.add_argument("--dry-run", action="store_true", help="só mostra o que mudaria")


def require(values: dict[str, str]) -> bool:
    """Confere se nenhum valor ficou vazio."""
    missing = [key for key, value in values.items() if not value]
    if missing:
        print(f"erro: informe {', '.join(missing)} (veja --help)", file=sys.stderr)
        return False
    return True


def finish(dry_run: bool, steps: list[str]) -> None:
    """Apaga este script e mostra os próximos passos."""
    if dry_run:
        return
    SELF.unlink()
    print("\nPronto. Próximos passos:")
    for number, step in enumerate(["Revise as mudanças com `git status` e `git diff`.", *steps], 1):
        print(f"  {number}. {step}")


def html_escape(text: str) -> str:
    """Escapa o texto para uso dentro do HTML e de atributos."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    owner, repo = remote_owner_repo()

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--title", default="", help="nome legível da organização")
    parser.add_argument("--tagline-en", default="", help="frase de apresentação em inglês")
    parser.add_argument("--tagline-pt", default="", help="frase de apresentação em português")
    common_arguments(parser, owner)
    args = parser.parse_args()

    interactive = not args.yes and sys.stdin.isatty()
    owner = ask("Dono no GitHub", args.owner, interactive)
    if repo and owner and repo.lower() != f"{owner}.github.io".lower():
        print(f"aviso: o GitHub Pages da organização exige o repositório {owner}.github.io (atual: {repo})")
    values = {
        "{{OWNER}}": owner,
        "{{TITLE}}": html_escape(ask("Nome legível", args.title or owner, interactive)),
        "{{TAGLINE_EN}}": html_escape(ask("Frase em inglês", args.tagline_en, interactive)),
        "{{TAGLINE_PT}}": html_escape(ask("Frase em português", args.tagline_pt, interactive)),
        "{{YEAR}}": str(date.today().year),
    }
    if not require(values):
        return 2

    print(f"Inicializando o portal {owner}.github.io{' [dry-run]' if args.dry_run else ''}")
    apply(values, args.dry_run)
    finish(
        args.dry_run,
        [
            "Troque img/logo.svg e a cor --brand em css/style.css.",
            "Troque os cartões de projetos em en/index.html e pt-br/index.html.",
            "Em Settings > Pages, escolha Source: GitHub Actions.",
            "Faça o commit inicial.",
        ],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
