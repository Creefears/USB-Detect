"""
Script de build pour USB Detect — génère l'exécutable via PyInstaller.

Usage:
    pip install pyinstaller
    python build.py
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
ICO_PATH = BASE_DIR / "usb_detect.ico"


def generate_ico():
    """Génère le fichier .ico depuis le SVG embarqué (nécessite Pillow)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow non installé, tentative d'installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageDraw

    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fond arrondi violet foncé
        margin = max(1, size // 16)
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=size // 5,
            fill=(42, 42, 74, 255),
        )

        # Connecteur USB simplifié (lignes blanches/violet clair)
        cx, cy = size // 2, size // 2
        color = (170, 170, 255, 255)

        # Ligne verticale
        lw = max(1, size // 16)
        x = cx
        draw.line([(x, size // 6), (x, cy + size // 6)], fill=color, width=lw)

        # Flèche en haut
        arrow = size // 6
        draw.line([(cx - arrow, size // 4), (cx, size // 8)], fill=color, width=lw)
        draw.line([(cx + arrow, size // 4), (cx, size // 8)], fill=color, width=lw)

        # Rectangle en bas (connecteur)
        rx1 = cx - size // 4
        ry1 = cy + size // 8
        rx2 = cx + size // 4
        ry2 = size - size // 6
        draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=max(1, size // 12), outline=color, width=lw)

        images.append(img)

    # Sauvegarder en .ico
    images[0].save(str(ICO_PATH), format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Icone generee : {ICO_PATH}")


def install_dependencies():
    """Installe les dépendances du projet et les outils de build."""
    req_file = BASE_DIR / "requirements.txt"
    if req_file.exists():
        print("Installation des dépendances (requirements.txt)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_exe():
    """Lance PyInstaller pour créer l'exécutable."""

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "USB Detect",
        "--add-data", f"config.example.json{';' if sys.platform == 'win32' else ':'}.",
        "--collect-all", "PyQt6",
        "--hidden-import", "wmi",
        "--hidden-import", "win32api",
        "--hidden-import", "win32con",
        "--hidden-import", "win32gui",
        "--hidden-import", "win32process",
        "--hidden-import", "psutil",
    ]

    if ICO_PATH.exists():
        cmd.extend(["--icon", str(ICO_PATH)])

    cmd.append("main.py")

    print("Lancement de PyInstaller...")
    print(" ".join(cmd))
    subprocess.check_call(cmd, cwd=str(BASE_DIR))
    print("\nBuild terminé ! L'exécutable se trouve dans le dossier dist/")


if __name__ == "__main__":
    print("=== USB Detect — Build ===\n")
    install_dependencies()
    generate_ico()
    build_exe()
    print()
    print("Pour installer dans Program Files, lancez :")
    print("  python installer.py")
