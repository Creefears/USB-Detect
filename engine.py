"""
USB Detect v2 - Moteur de détection et d'actions
Gère la config, le scan USB, les actions et les logs.
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
import threading
from dataclasses import dataclass, field
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, Optional

APP_VERSION = "2.1.0"
GITHUB_REPO = "Creefears/USB-Detect"
APP_NAME = "USB Detect"
INSTALL_DIR = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / APP_NAME

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
# EXE_DIR : dossier de l'exécutable (pour l'icône et les fichiers embarqués)
# DATA_DIR : dossier de données (config, log, lock) — %APPDATA% en prod
if getattr(sys, "frozen", False):
    EXE_DIR = Path(sys.executable).parent
    DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    DATA_DIR.mkdir(parents=True, exist_ok=True)
else:
    EXE_DIR = Path(__file__).parent
    DATA_DIR = EXE_DIR  # Mode dev → tout dans le dossier du projet

BASE_DIR = DATA_DIR  # Rétro-compatibilité (lock, etc.)
CONFIG_PATH = DATA_DIR / "config.json"
CONFIG_EXAMPLE_PATH = EXE_DIR / "config.example.json"  # Embarqué à côté de l'exe
LOG_PATH    = DATA_DIR / "usb_detect.log"
ICON_PATH   = EXE_DIR / "icon.png"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def setup_logging(enabled: bool = True) -> logging.Logger:
    logger = logging.getLogger("usb_detect")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    if enabled:
        handler = RotatingFileHandler(
            LOG_PATH, maxBytes=1_048_576, backupCount=1, encoding="utf-8"
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    # Console uniquement si un terminal est attaché (dev) — évite les erreurs en prod
    import sys
    if sys.stdout and sys.stdout.isatty():
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger

log = setup_logging()

# ---------------------------------------------------------------------------
# Modèles de données
# ---------------------------------------------------------------------------
@dataclass
class Action:
    type: str                        # run | close | command | file
    process: str = ""
    path: str = ""
    condition: str = ""              # "device_absent:Nom" | "device_present:Nom"
    post_sleep: float = 0
    wait_window: str = ""
    wait_window_action: str = ""     # close
    start_hidden: bool = False       # envoie WM_CLOSE pour aller en systray
    args: str = ""                   # arguments de lancement (ex: --minimized)

    @classmethod
    def from_dict(cls, d: dict) -> "Action":
        return cls(
            type=d.get("type", "run"),
            process=d.get("process", ""),
            path=d.get("path", ""),
            condition=d.get("condition", ""),
            post_sleep=d.get("post_sleep", 0),
            wait_window=d.get("wait_window", ""),
            wait_window_action=d.get("wait_window_action", ""),
            start_hidden=d.get("start_hidden", False),
            args=d.get("args", ""),
        )

    def to_dict(self) -> dict:
        return {k: v for k, v in {
            "type": self.type,
            "process": self.process,
            "path": self.path,
            "args": self.args if self.args else None,
            "condition": self.condition if self.condition else None,
            "post_sleep": self.post_sleep if self.post_sleep else None,
            "wait_window": self.wait_window if self.wait_window else None,
            "wait_window_action": self.wait_window_action if self.wait_window_action else None,
            "start_hidden": self.start_hidden if self.start_hidden else None,
        }.items() if v is not None}


@dataclass
class Device:
    name: str
    id: str
    match_type: str = "contains"     # contains | exact | regex
    confirm_on_disconnect: bool = False
    execution_condition: str = ""    # Condition globale d'exécution des actions
    enabled: bool = True             # Activer/désactiver le macro sans le supprimer
    on_connect: list[Action] = field(default_factory=list)
    on_disconnect: list[Action] = field(default_factory=list)
    connected: bool = False
    was_connected: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Device":
        return cls(
            name=d["name"],
            id=d["id"],
            match_type=d.get("match_type", "contains"),
            confirm_on_disconnect=d.get("confirm_on_disconnect", False),
            execution_condition=d.get("execution_condition", ""),
            enabled=d.get("enabled", True),
            on_connect=[Action.from_dict(a) for a in d.get("on_connect", [])],
            on_disconnect=[Action.from_dict(a) for a in d.get("on_disconnect", [])],
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "match_type": self.match_type,
            "confirm_on_disconnect": self.confirm_on_disconnect,
            "execution_condition": self.execution_condition,
            "enabled": self.enabled,
            "on_connect": [a.to_dict() for a in self.on_connect],
            "on_disconnect": [a.to_dict() for a in self.on_disconnect],
        }

    def is_present(self, raw_data: str) -> bool:
        if self.match_type == "exact":
            return self.id in raw_data.splitlines()
        elif self.match_type == "regex":
            return bool(re.search(self.id, raw_data))
        else:
            return self.id in raw_data


@dataclass
class Config:
    log_enabled: bool = True
    notifications_enabled: bool = True
    notification_duration: int = 4
    taskbar_setting: int = 0
    display_switch_command: str = ""
    display_switch_workdir: str = ""
    start_minimized: bool = True
    start_with_windows: bool = False
    start_in_tray: bool = True
    hidden_scan_ids: list[str] = field(default_factory=list)
    devices: list[Device] = field(default_factory=list)

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_PATH.exists():
            if CONFIG_EXAMPLE_PATH.exists():
                import shutil
                shutil.copy2(CONFIG_EXAMPLE_PATH, CONFIG_PATH)
                log.info("config.json créé à partir de config.example.json.")
            else:
                log.warning("config.json introuvable, configuration vide créée.")
                c = cls()
                c.save()
                return c
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        g = data.get("general", {})
        return cls(
            log_enabled=g.get("log_enabled", True),
            notifications_enabled=g.get("notifications_enabled", True),
            notification_duration=g.get("notification_duration", 4),
            taskbar_setting=g.get("taskbar_setting", 0),
            display_switch_command=g.get("display_switch_command", ""),
            display_switch_workdir=g.get("display_switch_workdir", ""),
            start_minimized=g.get("start_minimized", True),
            start_with_windows=g.get("start_with_windows", False),
            start_in_tray=g.get("start_in_tray", True),
            hidden_scan_ids=g.get("hidden_scan_ids", []),
            devices=[Device.from_dict(d) for d in data.get("devices", [])],
        )

    def save(self):
        data = {
            "general": {
                "log_enabled": self.log_enabled,
                "notifications_enabled": self.notifications_enabled,
                "notification_duration": self.notification_duration,
                "taskbar_setting": self.taskbar_setting,
                "display_switch_command": self.display_switch_command,
                "display_switch_workdir": self.display_switch_workdir,
                "start_minimized": self.start_minimized,
                "start_with_windows": self.start_with_windows,
                "start_in_tray": self.start_in_tray,
                "hidden_scan_ids": self.hidden_scan_ids,
            },
            "devices": [d.to_dict() for d in self.devices],
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info("Configuration sauvegardée.")

# ---------------------------------------------------------------------------
# Scanner USB (via WMI natif Python — sans PowerShell)
# ---------------------------------------------------------------------------
def _wmi_query(wql: str) -> list:
    """Exécute une requête WMI et retourne la liste des objets."""
    try:
        import wmi
        c = wmi.WMI()
        return c.query(wql)
    except Exception as e:
        log.error(f"Erreur WMI : {e}")
        return []


def scan_devices() -> str:
    """Retourne une chaîne concaténant tous les DeviceID + Name via WMI."""
    try:
        items = _wmi_query("SELECT DeviceID, Name FROM Win32_PNPEntity")
        lines = [f"{obj.DeviceID}  {obj.Name}" for obj in items if obj.DeviceID]
        return "\n".join(lines)
    except Exception as e:
        log.error(f"Erreur scan WMI : {e}")
        return ""


def get_device_type(device_id: str, name: str) -> str:
    """Retourne le type de périphérique basé sur son DeviceID et son nom."""
    uid = device_id.upper()
    n = (name or "").lower()
    if uid.startswith("DISPLAY\\") or uid.startswith("MONITOR\\"):
        return "monitor"
    if uid.startswith("STORAGE\\"):
        return "storage"
    if any(k in n for k in ("keyboard", "clavier")):
        return "keyboard"
    if any(k in n for k in ("mouse", "souris", "pointing")):
        return "mouse"
    if any(k in n for k in ("audio", "sound", "speaker", "micro", "headset", "headphone", "casque", "haut-parleur")):
        return "audio"
    if any(k in n for k in ("hub", "concentrateur")):
        return "hub"
    if any(k in n for k in ("gamepad", "controller", "manette", "joystick")):
        return "gamepad"
    if uid.startswith("HID\\"):
        return "hid"
    return "usb"


def get_monitor_count() -> int:
    try:
        import ctypes
        return int(ctypes.windll.user32.GetSystemMetrics(80))
    except Exception:
        return 0


def is_internal_device(device_id: str, name: str) -> bool:
    """Retourne True si le périphérique est probablement interne/système."""
    uid = device_id.upper()
    n = (name or "").lower()
    if uid.startswith("ROOT\\"):
        return True
    if uid.startswith("STORAGE\\"):
        return True
    if not name:
        return True
    if any(k in n for k in ("hub racine", "root hub", "concentrateur usb racine")):
        return True
    return False


def scan_usb_list(hidden_ids: list[str] = None) -> list[tuple[str, str]]:
    """Retourne [(device_id, name), ...] pour les périphériques USB/HID et moniteurs DISPLAY."""
    hidden = set(hidden_ids or [])
    try:
        items = _wmi_query(
            "SELECT DeviceID, Name FROM Win32_PNPEntity "
            "WHERE DeviceID LIKE 'USB%' OR DeviceID LIKE 'HID%' OR DeviceID LIKE 'DISPLAY%'"
        )
        results = []
        for obj in items:
            if obj.DeviceID and obj.DeviceID not in hidden:
                results.append((obj.DeviceID, obj.Name or ""))
        return sorted(results, key=lambda x: x[1].lower())
    except Exception as e:
        log.error(f"Erreur scan WMI : {e}")
        return []

# ---------------------------------------------------------------------------
# Processus — 100% via psutil, aucune fenêtre CMD
# ---------------------------------------------------------------------------
def is_process_running(process_name: str) -> bool:
    """Vérifie si un processus tourne, sans spawner de sous-processus."""
    import psutil
    name_lower = process_name.lower()
    try:
        return any(
            p.info["name"].lower() == name_lower
            for p in psutil.process_iter(["name"])
            if p.info["name"]
        )
    except Exception:
        return False


def run_process(process_name: str, path: str, args: str = ""):
    """Lance un exécutable sans fenêtre CMD visible.

    Si args est fourni (ex: '--minimized --no-sandbox'), il est ajouté après le chemin.
    La vérification "déjà en cours" reste active même avec des arguments.
    """
    if is_process_running(process_name):
        log.info(f"Déjà en cours : {process_name}")
        return
    log.info(f"Lancement : {process_name}" + (f"  args: {args}" if args else ""))

    # Construction de la commande : liste pour gérer les espaces dans le chemin
    import shlex
    cmd: list[str] | str
    if args.strip():
        cmd = [path] + shlex.split(args)
    else:
        cmd = path  # chaîne simple — compatibilité avec les raccourcis .lnk

    try:
        import win32con
        import win32process
        si = subprocess.STARTUPINFO()

        # SW_HIDE dans STARTUPINFO envoie nCmdShow=0 à l'app, ce qui peut
        # empêcher la logique "minimize → systray" de se déclencher.
        # → On ne force SW_HIDE QUE si aucun flag --minimized n'est présent.
        _has_min_flag = any(f in args for f in ("--minimized", "--start-minimized"))
        if not _has_min_flag:
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = win32con.SW_HIDE

        subprocess.Popen(
            cmd,
            startupinfo=si,
            creationflags=win32process.DETACHED_PROCESS,
            close_fds=True,
        )
    except Exception:
        # Fallback simple si win32 non dispo
        try:
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                close_fds=True,
            )
        except Exception as e:
            log.error(f"Impossible de lancer {process_name} : {e}")


def hide_process_windows(process_name: str, timeout: float = 12.0,
                          idle_cpu: float = 3.0, idle_duration: float = 1.5,
                          max_idle_wait: float = 25.0):
    """Cache puis ferme proprement les fenêtres du processus pour l'envoyer en systray.

    Étape 1 — Détection + SW_HIDE : attend l'apparition d'une fenêtre visible puis la cache.
    Étape 2 — Idle CPU dynamique  : au lieu d'un délai fixe, attend que le CPU du processus
                                     descende sous idle_cpu % pendant idle_duration s —
                                     signal que l'init est terminée et l'icône systray enregistrée.
                                     Timeout de sécurité : max_idle_wait secondes.
    Étape 3 — WM_CLOSE            : l'app gère la fermeture elle-même et va en systray.
    Étape 4 — Vérification        : confirme que le processus est toujours vivant.
    """
    try:
        import win32gui
        import win32con
        import win32process
        import psutil
    except ImportError:
        log.warning("win32gui/psutil non disponibles, start_hidden ignoré.")
        return

    name_lower = process_name.lower()
    deadline = time.time() + timeout

    # ── Étape 1 : attendre l'apparition d'une fenêtre visible puis la cacher ──
    hidden_hwnds: list[int] = []
    found_pids: set[int] = set()

    while time.time() < deadline:
        pids: set[int] = set()
        try:
            for p in psutil.process_iter(["name", "pid"]):
                if p.info["name"] and p.info["name"].lower() == name_lower:
                    pids.add(p.info["pid"])
        except Exception:
            pass

        if not pids:
            time.sleep(0.5)
            continue

        def _enum_cb(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            if not win32gui.GetWindowText(hwnd):
                return
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in pids:
                    hidden_hwnds.append(hwnd)
            except Exception:
                pass

        try:
            win32gui.EnumWindows(_enum_cb, None)
        except Exception:
            pass

        if hidden_hwnds:
            found_pids = pids
            for hwnd in hidden_hwnds:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                except Exception:
                    pass
            log.info(
                f"'{process_name}' : {len(hidden_hwnds)} fenêtre(s) cachée(s). "
                f"Attente idle CPU (< {idle_cpu}% pendant {idle_duration}s) avant WM_CLOSE…"
            )
            break

        time.sleep(0.5)
    else:
        log.warning(
            f"start_hidden : aucune fenêtre visible de '{process_name}' "
            f"trouvée après {timeout}s (peut-être déjà en systray)."
        )
        return

    # ── Étape 2 : attendre l'idle CPU (initialisation terminée) ───────────────
    # Récupérer les objets Process et initialiser leurs compteurs CPU (1er appel = baseline)
    procs: list = []
    try:
        for p in psutil.process_iter(["name", "pid"]):
            if p.info["pid"] in found_pids:
                p.cpu_percent()   # premier appel → retourne 0.0, initialise l'horloge interne
                procs.append(p)
    except Exception:
        pass

    idle_since: float | None = None
    wait_start = time.time()
    idle_deadline = wait_start + max_idle_wait

    while time.time() < idle_deadline:
        time.sleep(0.4)

        total_cpu = 0.0
        alive_count = 0
        for p in procs:
            try:
                total_cpu += p.cpu_percent()   # CPU depuis le dernier appel sur cet objet
                alive_count += 1
            except Exception:
                pass

        if alive_count == 0:
            log.warning(f"'{process_name}' s'est arrêté pendant l'attente idle.")
            return

        avg_cpu = total_cpu / alive_count

        if avg_cpu <= idle_cpu:
            if idle_since is None:
                idle_since = time.time()
            elif time.time() - idle_since >= idle_duration:
                elapsed = time.time() - wait_start
                log.info(
                    f"'{process_name}' idle ({avg_cpu:.1f}% CPU) "
                    f"après {elapsed:.1f}s → envoi WM_CLOSE."
                )
                break
        else:
            idle_since = None   # regain d'activité → reset du compteur idle
    else:
        elapsed = time.time() - wait_start
        log.info(
            f"'{process_name}' : timeout {elapsed:.0f}s atteint "
            f"→ envoi WM_CLOSE quand même."
        )

    # ── Étape 3 : envoyer WM_CLOSE aux fenêtres cachées ──
    for hwnd in hidden_hwnds:
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception:
            pass

    # ── Étape 4 : vérifier que le processus est toujours vivant (→ systray) ──
    time.sleep(2.0)
    still_alive = False
    try:
        for p in psutil.process_iter(["name"]):
            if p.info["name"] and p.info["name"].lower() == name_lower:
                still_alive = True
                break
    except Exception:
        pass

    if still_alive:
        log.info(f"'{process_name}' passé en systray (hide + WM_CLOSE).")
    else:
        log.warning(
            f"'{process_name}' s'est fermé au lieu d'aller en systray. "
            f"Désactivez 'Masquer la fenêtre' pour cette app."
        )


def close_process(process_name: str):
    """Ferme un processus via psutil, sans CMD."""
    import psutil
    name_lower = process_name.lower()
    found = False
    try:
        for p in psutil.process_iter(["name", "pid"]):
            if p.info["name"] and p.info["name"].lower() == name_lower:
                found = True
                try:
                    p.terminate()
                    p.wait(timeout=3)
                except psutil.TimeoutExpired:
                    p.kill()
                except Exception as e:
                    log.error(f"Erreur fermeture {process_name} : {e}")
    except Exception as e:
        log.error(f"Erreur itération processus : {e}")
    if found:
        log.info(f"Fermé : {process_name}")

# ---------------------------------------------------------------------------
# Moteur principal
# ---------------------------------------------------------------------------
class Engine:
    def __init__(self, config: Config):
        self.config = config
        # Callbacks vers l'UI (appelés depuis le thread worker via QTimer.singleShot)
        self.on_device_changed: Optional[Callable] = None   # (device) -> None
        self.on_confirm_needed: Optional[Callable] = None   # (device) -> bool  [DOIT être thread-safe]
        self.on_notify: Optional[Callable] = None           # (title, text) -> None
        self.monitor_count: int = 0

    def scan_and_update(self, first_run: bool = False):
        self.monitor_count = get_monitor_count()
        log.info(f"Moniteurs actifs détectés: {self.monitor_count}")
        raw = scan_devices()
        for device in self.config.devices:
            device.connected = device.is_present(raw)
        for device in self.config.devices:
            if device.connected and device.execution_condition and not self._check_condition(device.execution_condition):
                device.connected = False

        if first_run:
            for device in self.config.devices:
                device.was_connected = device.connected
                if not device.enabled:
                    continue
                threading.Thread(
                    target=self._execute_actions,
                    args=(device, device.on_connect if device.connected else device.on_disconnect),
                    daemon=True,
                ).start()
        else:
            for device in self.config.devices:
                changed = device.connected != device.was_connected

                if not device.enabled:
                    device.was_connected = device.connected
                    if changed and self.on_device_changed:
                        self.on_device_changed(device)
                    continue

                if device.connected and not device.was_connected:
                    log.info(f"Connecté : {device.name}")
                    self._notify("Connecté", f"{device.name} détecté")
                    threading.Thread(
                        target=self._execute_actions,
                        args=(device, device.on_connect),
                        daemon=True,
                    ).start()

                elif not device.connected and device.was_connected:
                    self._notify("Déconnecté", f"{device.name} retiré")
                    if device.confirm_on_disconnect and self.on_confirm_needed:
                        confirmed = self.on_confirm_needed(device)
                        if confirmed:
                            log.info(f"Déconnecté (confirmé) : {device.name}")
                            threading.Thread(
                                target=self._execute_actions,
                                args=(device, device.on_disconnect),
                                daemon=True,
                            ).start()
                        else:
                            log.warning(f"Déconnexion annulée : {device.name}")
                    else:
                        log.info(f"Déconnecté : {device.name}")
                        threading.Thread(
                            target=self._execute_actions,
                            args=(device, device.on_disconnect),
                            daemon=True,
                        ).start()

                device.was_connected = device.connected

                if changed and self.on_device_changed:
                    self.on_device_changed(device)

    def _check_condition(self, condition: str) -> bool:
        """Évalue une condition ou plusieurs conditions séparées par && (logique ET)."""
        if not condition:
            return True
        parts = [p.strip() for p in condition.split("&&") if p.strip()]
        return all(self._check_single_condition(p) for p in parts)

    def _check_single_condition(self, condition: str) -> bool:
        if not condition:
            return True
        m = re.match(r"monitors\s*(==|>=|<=|>|<)\s*(\d+)", condition)
        if m:
            op, val = m.group(1), int(m.group(2))
            count = self.monitor_count
            result = False
            if op == "==":
                result = count == val
            elif op == ">=":
                result = count >= val
            elif op == "<=":
                result = count <= val
            elif op == ">":
                result = count > val
            elif op == "<":
                result = count < val
            log.info(f"Condition monitors '{condition}' évaluée avec {count} écrans -> {result}")
            return result
        m = re.match(r"device_(absent|present):(.+)", condition)
        if m:
            mode, name = m.group(1), m.group(2).strip()
            dev = next((d for d in self.config.devices if d.name == name), None)
            if dev is None:
                log.warning(f"Condition référence un device inconnu : '{name}'")
                return True
            return (not dev.connected) if mode == "absent" else dev.connected
        log.warning(f"Condition non reconnue : '{condition}'")
        return False

    def _execute_actions(self, device: Device, actions: list[Action]):
        """Exécute les actions dans un thread dédié — ne bloque JAMAIS le ScanWorker."""
        if device.execution_condition and not self._check_condition(device.execution_condition):
            log.info(f"Condition d'exécution non remplie pour {device.name}, actions annulées")
            return
        if device.execution_condition:
            log.info(f"Conditions d'exécution remplies pour {device.name}: '{device.execution_condition}'")
        for action in actions:
            if not self._check_condition(action.condition):
                continue
            if action.type == "run":
                run_process(action.process, action.path, action.args)
                if action.start_hidden:
                    import threading
                    threading.Thread(
                        target=hide_process_windows,
                        args=(action.process,),
                        daemon=True,
                    ).start()
                # Fix #3 : time.sleep ici est OK car on est dans un thread dédié
                if action.post_sleep:
                    time.sleep(action.post_sleep)
                if action.wait_window:
                    self._wait_for_window(action.wait_window, action.wait_window_action)
            elif action.type == "close":
                close_process(action.process)
            elif action.type in ("command", "file"):
                try:
                    subprocess.Popen(
                        action.path,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        close_fds=True,
                    )
                except Exception as e:
                    log.error(f"Erreur action {action.type} : {e}")

    def _wait_for_window(self, title: str, action: str, timeout: int = 15):
        """Attend l'apparition d'une fenêtre (thread dédié — pas de blocage du scan)."""
        try:
            import win32gui
        except ImportError:
            log.warning("win32gui non disponible, wait_window ignoré.")
            return
        deadline = time.time() + timeout
        while time.time() < deadline:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                log.info(f"Fenêtre trouvée : '{title}'")
                if action == "close":
                    win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                return
            time.sleep(0.5)
        log.warning(f"Timeout : fenêtre '{title}' non trouvée après {timeout}s")

    def _notify(self, title: str, text: str):
        if self.config.notifications_enabled and self.on_notify:
            self.on_notify(title, text)

    def apply_taskbar(self):
        """Applique le réglage de groupement de la barre des tâches."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                0, winreg.KEY_SET_VALUE
            )
            val = 0 if self.config.taskbar_setting == 0 else 1
            winreg.SetValueEx(key, "TaskbarGlomLevel", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(key)
        except Exception as e:
            log.error(f"Erreur registre taskbar : {e}")


# ---------------------------------------------------------------------------
# Démarrage avec Windows (registre Run)
# ---------------------------------------------------------------------------
_STARTUP_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_STARTUP_APP_NAME = "USBDetect"


def get_exe_path() -> str:
    """Retourne le chemin de l'exécutable ou du script pour le démarrage."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return f'"{sys.executable}" "{Path(__file__).parent / "main.py"}"'


def set_startup_enabled(enabled: bool):
    """Ajoute ou supprime USB Detect du démarrage Windows."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _STARTUP_REG_KEY,
            0, winreg.KEY_SET_VALUE
        )
        if enabled:
            winreg.SetValueEx(key, _STARTUP_APP_NAME, 0, winreg.REG_SZ, get_exe_path())
            log.info("Démarrage avec Windows activé.")
        else:
            try:
                winreg.DeleteValue(key, _STARTUP_APP_NAME)
            except FileNotFoundError:
                pass
            log.info("Démarrage avec Windows désactivé.")
        winreg.CloseKey(key)
    except Exception as e:
        log.error(f"Erreur registre startup : {e}")


def is_startup_enabled() -> bool:
    """Vérifie si USB Detect est dans le démarrage Windows."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _STARTUP_REG_KEY,
            0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, _STARTUP_APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Vérification des mises à jour GitHub
# ---------------------------------------------------------------------------
def check_for_update(callback: Optional[Callable] = None):
    """Vérifie si une nouvelle version est disponible sur GitHub.

    Appelle callback(latest_version, download_url, asset_url) si une mise à jour
    est dispo, ou callback(None, None, None) sinon.
    """
    def _check():
        try:
            import urllib.request
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "").lstrip("vV")
            html_url = data.get("html_url", "")
            # Chercher l'asset .exe dans la release
            asset_url = ""
            for asset in data.get("assets", []):
                if asset.get("name", "").lower().endswith(".exe"):
                    asset_url = asset.get("browser_download_url", "")
                    break
            if tag and tag != APP_VERSION:
                log.info(f"Mise à jour disponible : v{tag} (actuel: v{APP_VERSION})")
                if callback:
                    callback(tag, html_url, asset_url)
            else:
                log.info(f"Aucune mise à jour (v{APP_VERSION} est à jour).")
                if callback:
                    callback(None, None, None)
        except Exception as e:
            log.warning(f"Impossible de vérifier les mises à jour : {e}")
            if callback:
                callback(None, None, None)

    threading.Thread(target=_check, daemon=True).start()


def download_and_apply_update(asset_url: str, progress_callback: Optional[Callable] = None,
                              done_callback: Optional[Callable] = None):
    """Télécharge le .exe depuis GitHub et remplace l'exécutable actuel.

    - progress_callback(percent: int, status: str) pour la progression
    - done_callback(success: bool, error: str) quand c'est terminé
    """
    def _download():
        import urllib.request
        import tempfile
        import shutil

        try:
            if progress_callback:
                progress_callback(0, "Connexion au serveur…")

            req = urllib.request.Request(asset_url)
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536

                # Télécharger dans un fichier temporaire
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".exe",
                                                  dir=str(DATA_DIR))
                tmp_path = tmp.name
                try:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        tmp.write(chunk)
                        downloaded += len(chunk)
                        if total > 0 and progress_callback:
                            pct = int(downloaded * 100 / total)
                            mb = downloaded / (1024 * 1024)
                            total_mb = total / (1024 * 1024)
                            progress_callback(pct, f"{mb:.1f} / {total_mb:.1f} Mo")
                finally:
                    tmp.close()

            if progress_callback:
                progress_callback(100, "Téléchargement terminé, installation…")

            # Déterminer le chemin de l'exe actuel
            if getattr(sys, "frozen", False):
                current_exe = sys.executable
            else:
                # Mode dev : on place le .exe à côté dans dist/
                dist_dir = EXE_DIR / "dist"
                dist_dir.mkdir(exist_ok=True)
                current_exe = str(dist_dir / "USB Detect.exe")

            # Créer un script batch qui remplace l'exe après fermeture
            bat_path = str(DATA_DIR / "_update.bat")
            with open(bat_path, "w", encoding="utf-8") as bat:
                bat.write("@echo off\n")
                bat.write("echo Mise a jour de USB Detect...\n")
                bat.write("timeout /t 2 /nobreak >nul\n")
                bat.write(f'copy /y "{tmp_path}" "{current_exe}"\n')
                bat.write(f'del "{tmp_path}"\n')
                bat.write(f'start "" "{current_exe}"\n')
                bat.write(f'del "%~f0"\n')

            log.info(f"Mise à jour téléchargée : {tmp_path} → {current_exe}")

            if done_callback:
                done_callback(True, bat_path)

        except Exception as e:
            log.error(f"Erreur de téléchargement : {e}")
            if done_callback:
                done_callback(False, str(e))

    threading.Thread(target=_download, daemon=True).start()


# ---------------------------------------------------------------------------
# Auto-installation dans Program Files
# ---------------------------------------------------------------------------
def _parse_version(v: str) -> tuple:
    """Transforme '2.1.0' en (2, 1, 0) pour comparaison."""
    try:
        return tuple(int(x) for x in v.strip().lstrip("vV").split("."))
    except Exception:
        return (0, 0, 0)


def is_installed() -> bool:
    """Vérifie si l'exe tourne depuis le dossier d'installation."""
    if not getattr(sys, "frozen", False):
        return True  # Mode dev → pas d'install
    try:
        exe_dir = Path(sys.executable).resolve().parent
        target = INSTALL_DIR.resolve()
        return exe_dir == target
    except Exception:
        return False


def get_installed_version() -> Optional[str]:
    """Lit la version installée dans le registre. Retourne None si pas installé."""
    try:
        import winreg as _wr
        with _wr.OpenKey(_wr.HKEY_LOCAL_MACHINE,
                         r"Software\Microsoft\Windows\CurrentVersion\Uninstall\USBDetect",
                         0, _wr.KEY_READ) as key:
            val, _ = _wr.QueryValueEx(key, "DisplayVersion")
            return val
    except Exception:
        return None


def check_install_status() -> str:
    """Détermine l'action à effectuer au lancement.

    Retourne :
      'run'     — déjà installé, lancer normalement
      'install' — première installation
      'update'  — version plus récente que celle installée
      'older'   — version plus ancienne que celle installée (ne rien faire)
    """
    if not getattr(sys, "frozen", False):
        return "run"  # Mode dev
    if is_installed():
        return "run"  # Lancé depuis Program Files

    installed_ver = get_installed_version()
    if installed_ver is None:
        return "install"

    current = _parse_version(APP_VERSION)
    installed = _parse_version(installed_ver)
    if current > installed:
        return "update"
    elif current < installed:
        return "older"
    else:
        return "run"  # Même version, juste lancer l'installé


def self_install(is_update: bool = False) -> Optional[str]:
    """Copie l'exe dans Program Files et configure Windows.

    Si is_update=True, remplace l'exe existant sans toucher à la config.
    Retourne le chemin de l'exe installé, ou None en cas d'échec.
    Doit être appelé avec les droits admin.
    """
    import shutil

    current_exe = Path(sys.executable).resolve()

    # Créer le dossier d'installation
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    dest_exe = INSTALL_DIR / "USB Detect.exe"

    # Copier l'exe (remplace s'il existe déjà)
    shutil.copy2(str(current_exe), str(dest_exe))

    # Extraire config.example.json si embarqué par PyInstaller
    internal_data = getattr(sys, "_MEIPASS", None)
    if internal_data:
        example_src = Path(internal_data) / "config.example.json"
        if example_src.exists():
            dest_example = INSTALL_DIR / "config.example.json"
            # Toujours mettre à jour l'exemple
            shutil.copy2(str(example_src), str(dest_example))

    # Raccourci dans le menu Démarrer (créer ou mettre à jour)
    _create_start_menu_shortcut(str(dest_exe))

    # Enregistrement dans Ajout/Suppression de programmes (met à jour la version)
    _register_uninstall(str(dest_exe))

    return str(dest_exe)


def self_uninstall():
    """Supprime l'installation (appelé via l'app ou la ligne de commande)."""
    import shutil
    import winreg as _wr

    # Sauvegarder config sur le bureau (depuis AppData)
    appdata_dir = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    config_path = appdata_dir / "config.json"
    if config_path.exists():
        backup = Path.home() / "Desktop" / "usb_detect_config_backup.json"
        shutil.copy2(str(config_path), str(backup))
        log.info(f"Config sauvegardée : {backup}")

    # Supprimer le dossier AppData
    if appdata_dir.exists():
        shutil.rmtree(str(appdata_dir), ignore_errors=True)

    # Raccourci menu Démarrer
    start_menu = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / \
        "Microsoft" / "Windows" / "Start Menu" / "Programs"
    lnk = start_menu / "USB Detect.lnk"
    if lnk.exists():
        lnk.unlink()

    # Registre : Ajout/Suppression
    try:
        _wr.DeleteKey(_wr.HKEY_LOCAL_MACHINE,
                      r"Software\Microsoft\Windows\CurrentVersion\Uninstall\USBDetect")
    except FileNotFoundError:
        pass

    # Registre : démarrage auto
    try:
        with _wr.OpenKey(_wr.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, _wr.KEY_SET_VALUE) as k:
            _wr.DeleteValue(k, "USBDetect")
    except FileNotFoundError:
        pass

    # Créer un batch qui supprimera le dossier Program Files après fermeture
    bat = INSTALL_DIR / "_cleanup.bat"
    bat.write_text(
        "@echo off\n"
        "timeout /t 2 /nobreak >nul\n"
        f'rmdir /s /q "{INSTALL_DIR}"\n'
        'del "%~f0"\n',
        encoding="utf-8"
    )
    subprocess.Popen(
        ["cmd", "/c", str(bat)],
        creationflags=0x08000000  # CREATE_NO_WINDOW
    )


def _create_start_menu_shortcut(exe_path: str):
    """Crée un raccourci .lnk dans le menu Démarrer."""
    start_menu = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / \
        "Microsoft" / "Windows" / "Start Menu" / "Programs"
    lnk = start_menu / "USB Detect.lnk"
    ico = INSTALL_DIR / "usb_detect.ico"
    ps_cmd = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$s = $ws.CreateShortcut("{lnk}"); '
        f'$s.TargetPath = "{exe_path}"; '
        f'$s.WorkingDirectory = "{INSTALL_DIR}"; '
        f'$s.Description = "Surveillance USB en temps réel"; '
    )
    if ico.exists():
        ps_cmd += f'$s.IconLocation = "{ico}"; '
    ps_cmd += '$s.Save()'
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            check=True, creationflags=0x08000000
        )
    except Exception as e:
        log.warning(f"Raccourci non créé : {e}")


def _register_uninstall(exe_path: str):
    """Enregistre le programme dans Ajout/Suppression de programmes."""
    import winreg as _wr
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\USBDetect"
    try:
        with _wr.CreateKey(_wr.HKEY_LOCAL_MACHINE, key_path) as key:
            _wr.SetValueEx(key, "DisplayName", 0, _wr.REG_SZ, APP_NAME)
            _wr.SetValueEx(key, "Publisher", 0, _wr.REG_SZ, "Creefears")
            _wr.SetValueEx(key, "DisplayVersion", 0, _wr.REG_SZ, APP_VERSION)
            _wr.SetValueEx(key, "InstallLocation", 0, _wr.REG_SZ, str(INSTALL_DIR))
            ico = INSTALL_DIR / "usb_detect.ico"
            if ico.exists():
                _wr.SetValueEx(key, "DisplayIcon", 0, _wr.REG_SZ, str(ico))
            _wr.SetValueEx(key, "UninstallString", 0, _wr.REG_SZ,
                           f'"{exe_path}" --uninstall')
            _wr.SetValueEx(key, "NoModify", 0, _wr.REG_DWORD, 1)
            _wr.SetValueEx(key, "NoRepair", 0, _wr.REG_DWORD, 1)
            exe_size = Path(exe_path).stat().st_size // 1024
            _wr.SetValueEx(key, "EstimatedSize", 0, _wr.REG_DWORD, exe_size)
    except PermissionError:
        log.warning("Impossible d'enregistrer dans Ajout/Suppression (droits admin)")
