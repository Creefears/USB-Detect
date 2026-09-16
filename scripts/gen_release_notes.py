#!/usr/bin/env python3
"""Génère les notes de version à partir du CHANGELOG de engine.py.

Le CHANGELOG qui alimente la fenêtre « Quoi de neuf » sert de source unique :
les notes de release en sont dérivées, en français et en anglais (via le
dictionnaire de traduction de i18n.py).

Usage :
    python scripts/gen_release_notes.py v2.4.0
    python scripts/gen_release_notes.py 2.4.0 > notes.md

Les fichiers sont analysés avec `ast` plutôt qu'importés : aucune dépendance
(PyQt6, pywin32…) n'est requise, et rien n'est exécuté.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _literal_assign(py_file: Path, name: str):
    """Retourne la valeur littérale affectée à `name` dans `py_file`."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise SystemExit(f"'{name}' introuvable dans {py_file.name}")


def normalize(version: str) -> str:
    return version.strip().lstrip("vV")


def build_notes(version: str) -> str:
    version = normalize(version)
    changelog = _literal_assign(ROOT / "engine.py", "CHANGELOG")
    entries = changelog.get(version)

    if not entries:
        available = ", ".join(sorted(changelog, reverse=True))
        raise SystemExit(
            f"Aucune entrée CHANGELOG pour la version {version}.\n"
            f"Versions disponibles : {available}\n"
            f"Ajoutez une entrée dans CHANGELOG (engine.py) avant de publier."
        )

    # Traductions anglaises (repli sur le français si absente)
    try:
        en_map = _literal_assign(ROOT / "i18n.py", "_EN")
    except SystemExit:
        en_map = {}

    fr_items = "\n".join(f"- {e}" for e in entries)
    en_items = "\n".join(f"- {en_map.get(e, e)}" for e in entries)

    return f"""## ✨ Nouveautés

{fr_items}

## 🔄 Mise à jour

Votre configuration (macros, paramètres) est **préservée** lors de la mise à jour.

### Installation
Téléchargez `USB Detect.exe` ci-dessous et lancez-le : l'installateur s'occupe du reste.

---

<details>
<summary><b>🇬🇧 English</b></summary>

## ✨ What's new

{en_items}

## 🔄 Update

Your configuration (macros, settings) is **preserved** across updates.

### Installation
Download `USB Detect.exe` below and run it — the installer takes care of the rest.

</details>
"""


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage : python scripts/gen_release_notes.py <version>")
    sys.stdout.write(build_notes(sys.argv[1]))


if __name__ == "__main__":
    main()
