"""
Installateur Windows pour USB Detect.

Installe l'application dans Program Files, crée un raccourci dans le menu
Démarrer et enregistre le programme dans Ajout/Suppression de programmes.

Doit être lancé en tant qu'administrateur :
    python installer.py          — installe
    python installer.py --remove — désinstalle
"""

import ctypes
import os
import shutil
import sys
import winreg
from pathlib import Path


APP_NAME = "USB Detect"
APP_PUBLISHER = "Creefears"
APP_EXE = "USB Detect.exe"
INSTALL_DIR = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / APP_NAME
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\USBDetect"


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """Relance ce script avec élévation UAC."""
    params = " ".join(f'"{a}"' for a in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{__file__}" {params}', None, 1
    )
    sys.exit(0)


def find_exe() -> Path:
    """Cherche l'exe compilé dans dist/ à côté de ce script."""
    base = Path(__file__).parent
    candidates = [
        base / "dist" / APP_EXE,
        base / APP_EXE,
    ]
    for p in candidates:
        if p.exists():
            return p
    print(f"ERREUR : {APP_EXE} introuvable dans dist/ ou le dossier courant.")
    print("Lancez d'abord : python build.py")
    sys.exit(1)


def create_shortcut(target: str, shortcut_path: str, icon: str = "", description: str = ""):
    """Crée un raccourci Windows (.lnk)."""
    import subprocess
    ps = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$s = $ws.CreateShortcut("{shortcut_path}"); '
        f'$s.TargetPath = "{target}"; '
        f'$s.WorkingDirectory = "{Path(target).parent}"; '
    )
    if icon:
        ps += f'$s.IconLocation = "{icon}"; '
    if description:
        ps += f'$s.Description = "{description}"; '
    ps += '$s.Save()'
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        check=True, creationflags=0x08000000
    )


def install():
    print(f"=== Installation de {APP_NAME} ===\n")

    exe_src = find_exe()
    ico_src = Path(__file__).parent / "usb_detect.ico"
    config_example = Path(__file__).parent / "config.example.json"

    # 1. Créer le dossier d'installation
    print(f"Dossier : {INSTALL_DIR}")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Copier l'exe
    dest_exe = INSTALL_DIR / APP_EXE
    print(f"Copie de {exe_src.name}...")
    shutil.copy2(str(exe_src), str(dest_exe))

    # 3. Copier l'icône si elle existe
    dest_ico = INSTALL_DIR / "usb_detect.ico"
    if ico_src.exists():
        shutil.copy2(str(ico_src), str(dest_ico))

    # 4. Copier config.example.json (le vrai config.json sera créé au 1er lancement)
    if config_example.exists():
        shutil.copy2(str(config_example), str(INSTALL_DIR / "config.example.json"))

    # 5. Raccourci menu Démarrer
    start_menu = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    shortcut_path = start_menu / f"{APP_NAME}.lnk"
    print(f"Raccourci : {shortcut_path}")
    try:
        create_shortcut(
            str(dest_exe), str(shortcut_path),
            icon=str(dest_ico) if dest_ico.exists() else "",
            description="Surveillance USB en temps réel"
        )
    except Exception as e:
        print(f"  Avertissement raccourci : {e}")

    # 6. Enregistrement dans Ajout/Suppression de programmes
    print("Enregistrement dans Windows...")
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, UNINSTALL_KEY) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_PUBLISHER)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(dest_ico))
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(INSTALL_DIR))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                              f'"{sys.executable}" "{Path(__file__).resolve()}" --remove')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            # Taille approximative en Ko
            exe_size = dest_exe.stat().st_size // 1024
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, exe_size)
    except PermissionError:
        print("  Impossible d'écrire dans le registre (droits admin requis)")

    print(f"\nInstallation terminée !")
    print(f"  Emplacement : {INSTALL_DIR}")
    print(f"  Lancez depuis le menu Démarrer ou : \"{dest_exe}\"")


def uninstall():
    print(f"=== Désinstallation de {APP_NAME} ===\n")

    # Supprimer le raccourci
    start_menu = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    shortcut = start_menu / f"{APP_NAME}.lnk"
    if shortcut.exists():
        shortcut.unlink()
        print(f"Raccourci supprimé : {shortcut}")

    # Supprimer l'entrée registre
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, UNINSTALL_KEY)
        print("Entrée registre supprimée")
    except FileNotFoundError:
        pass

    # Supprimer le dossier (sauf config.json pour garder les macros)
    if INSTALL_DIR.exists():
        config_path = INSTALL_DIR / "config.json"
        if config_path.exists():
            backup = Path.home() / "Desktop" / "usb_detect_config_backup.json"
            shutil.copy2(str(config_path), str(backup))
            print(f"Configuration sauvegardée sur le bureau : {backup}")
        shutil.rmtree(str(INSTALL_DIR), ignore_errors=True)
        print(f"Dossier supprimé : {INSTALL_DIR}")

    # Supprimer l'entrée de démarrage auto
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "USBDetect")
            print("Démarrage automatique désactivé")
    except FileNotFoundError:
        pass

    print("\nDésinstallation terminée !")


if __name__ == "__main__":
    if not is_admin():
        print("Droits administrateur requis. Demande d'élévation...")
        run_as_admin()

    if "--remove" in sys.argv or "--uninstall" in sys.argv:
        uninstall()
    else:
        install()

    input("\nAppuyez sur Entrée pour fermer...")
