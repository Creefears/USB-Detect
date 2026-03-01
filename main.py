"""
USB Detect v2 - Interface principale PyQt6
"""

import sys
import os
import webbrowser
from pathlib import Path

from PyQt6.QtCore import QSize, QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMessageBox, QProgressBar, QPushButton,
    QScrollArea, QSystemTrayIcon, QTextEdit, QVBoxLayout, QWidget,
)

from engine import (
    APP_VERSION, BASE_DIR, CONFIG_PATH, INSTALL_DIR, Config, Device, Engine,
    get_device_type, log, check_for_update, download_and_apply_update,
    set_startup_enabled, is_startup_enabled, check_install_status,
    self_install, self_uninstall, get_installed_version,
)
from wizard import DeviceWizard

# ---------------------------------------------------------------------------
# Stylesheet global (thème sombre)
# ---------------------------------------------------------------------------
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #f0f0f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}
QPushButton {
    background: #2a2a3e;
    color: #f0f0f0;
    border: 1px solid #3a3a4a;
    border-radius: 6px;
    padding: 5px 14px;
}
QPushButton:hover   { background: #3a3a5a; border-color: #5050aa; }
QPushButton:pressed { background: #5050aa; }
QPushButton#primary {
    background: #5050aa;
    border-color: #6060cc;
}
QPushButton#primary:hover { background: #6060cc; }
QLabel#title {
    font-size: 12pt;
    font-weight: bold;
    color: #c0c0ff;
}
QLabel#subtitle {
    font-size: 9pt;
    color: #888888;
}
QScrollArea { border: none; }
QMenu {
    background: #2a2a3e;
    color: #f0f0f0;
    border: 1px solid #3a3a4a;
    border-radius: 4px;
}
QMenu::item:selected { background: #5050aa; }
QMenu::separator { background: #3a3a4a; height: 1px; margin: 4px 8px; }
"""

# ---------------------------------------------------------------------------
# Génération d'icônes via SVG → QIcon (sans fichier externe)
# ---------------------------------------------------------------------------
def make_svg_icon(svg: str, size: int = 20) -> QIcon:
    """Convertit un SVG string en QIcon."""
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)


def icon_usb() -> QIcon:
    """Icône USB — indicateur de type périphérique."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="#8888cc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2v12"/>
        <path d="M8 6l4-4 4 4"/>
        <path d="M6 15h12a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2z"/>
        <line x1="9" y1="11" x2="9" y2="14"/>
        <line x1="15" y1="9" x2="15" y2="14"/>
        <circle cx="9" cy="10" r="1" fill="#8888cc" stroke="none"/>
        <circle cx="15" cy="8" r="1" fill="#8888cc" stroke="none"/>
    </svg>'''
    return make_svg_icon(svg, 18)


def icon_monitor() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>'''
    return make_svg_icon(svg, 18)

def icon_keyboard() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="6" width="20" height="13" rx="2"/><line x1="6" y1="10" x2="6.01" y2="10"/><line x1="10" y1="10" x2="10.01" y2="10"/><line x1="14" y1="10" x2="14.01" y2="10"/><line x1="18" y1="10" x2="18.01" y2="10"/><line x1="6" y1="14" x2="18" y2="14"/></svg>'''
    return make_svg_icon(svg, 18)

def icon_mouse() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="1.8" stroke-linecap="round"><path d="M6 10a6 6 0 0 1 12 0v5a6 6 0 0 1-12 0v-5z"/><line x1="12" y1="4" x2="12" y2="11"/><line x1="6" y1="10.5" x2="18" y2="10.5"/></svg>'''
    return make_svg_icon(svg, 18)

def icon_hub() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><line x1="12" y1="9" x2="12" y2="3"/><line x1="14.6" y1="13.5" x2="20" y2="17"/><line x1="9.4" y1="13.5" x2="4" y2="17"/></svg>'''
    return make_svg_icon(svg, 18)

def icon_audio() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="1.8" stroke-linecap="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>'''
    return make_svg_icon(svg, 18)

def icon_gamepad() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="1.8" stroke-linecap="round"><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="11" x2="15.01" y2="11"/><line x1="18" y1="13" x2="18.01" y2="13"/><path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59l-.9 7.9A4 4 0 0 0 5.78 21a4 4 0 0 0 3.58-2.21L10 17h4l.64 1.79A4 4 0 0 0 18.22 21a4 4 0 0 0 3.978-4.51l-.9-7.9A4 4 0 0 0 17.32 5z"/></svg>'''
    return make_svg_icon(svg, 18)

_DEVICE_ICONS = {
    "monitor":  icon_monitor,
    "keyboard": icon_keyboard,
    "mouse":    icon_mouse,
    "hub":      icon_hub,
    "audio":    icon_audio,
    "gamepad":  icon_gamepad,
    "hid":      icon_usb,
    "usb":      icon_usb,
    "storage":  icon_usb,
}


def icon_edit() -> QIcon:
    """Crayon — bouton Modifier."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="#8888ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>'''
    return make_svg_icon(svg)


def icon_delete() -> QIcon:
    """Corbeille — bouton Supprimer."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="#dd4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
        <path d="M10 11v6M14 11v6"/>
        <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
    </svg>'''
    return make_svg_icon(svg)


def _make_window_icon() -> QIcon:
    """Icône USB colorée pour la barre de titre et la barre des tâches Windows."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
        <!-- Fond arrondi violet foncé -->
        <rect x="1" y="1" width="30" height="30" rx="7" fill="#2a2a4a"/>
        <!-- Connecteur USB blanc/violet clair -->
        <g stroke="#aaaaff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none">
            <line x1="16" y1="4" x2="16" y2="18"/>
            <polyline points="12,8 16,4 20,8"/>
            <rect x="10" y="18" width="12" height="8" rx="2" stroke="#aaaaff"/>
            <line x1="13" y1="14" x2="13" y2="18"/>
            <line x1="19" y1="12" x2="19" y2="18"/>
            <circle cx="13" cy="13" r="1.2" fill="#aaaaff" stroke="none"/>
            <circle cx="19" cy="11" r="1.2" fill="#aaaaff" stroke="none"/>
        </g>
    </svg>'''
    return make_svg_icon(svg, 32)


def make_circle_icon(color: str, size: int = 16) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    margin = 2
    painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
    painter.end()
    return QIcon(pix)


def make_tray_icon(any_connected: bool) -> QIcon:
    color = "#00cc66" if any_connected else "#dd4444"
    size = 22
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(3, 3, size - 6, size - 6)
    painter.end()
    return QIcon(pix)


# ---------------------------------------------------------------------------
# Visionneuse de logs interne
# ---------------------------------------------------------------------------
class LogViewer(QDialog):
    """Fenêtre non-modale affichant les logs en temps réel avec coloration par niveau."""

    # Couleurs HTML par niveau de log
    _LEVEL_COLORS = {
        "[ERROR]":   "#ff6666",
        "[WARNING]": "#ffaa44",
        "[INFO]":    "#66cc88",
        "[DEBUG]":   "#8888aa",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋  Logs — USB Detect")
        self.setMinimumSize(700, 420)
        self.resize(800, 500)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        self._raw_lines: list[str] = []
        self._last_size: int = -1
        self._cleared = False  # si l'utilisateur a vidé la vue

        self._build_ui()
        self._load_log()

        # Timer de rafraîchissement auto (2s)
        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._refresh)
        self._timer.start()

    def _build_ui(self):
        from PyQt6.QtWidgets import QFrame
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # --- Barre d'outils ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("🔍  Filtrer les lignes…")
        self.filter_edit.setToolTip("Affiche uniquement les lignes contenant ce texte")
        self.filter_edit.textChanged.connect(self._apply_filter)
        self.filter_edit.setStyleSheet(
            "QLineEdit { background: #22223a; border: 1px solid #3a3a5a; "
            "border-radius: 4px; padding: 4px 8px; color: #d0d0e0; }"
            "QLineEdit:focus { border-color: #6060cc; }"
        )

        scroll_btn = QPushButton("⬆  Aller en haut")
        scroll_btn.setToolTip("Défiler jusqu'à la dernière entrée de log")
        scroll_btn.setFixedHeight(28)
        scroll_btn.clicked.connect(self._scroll_to_top)

        clear_btn = QPushButton("🗑  Effacer la vue")
        clear_btn.setToolTip("Vider l'affichage (ne supprime pas le fichier de log)")
        clear_btn.setFixedHeight(28)
        clear_btn.setStyleSheet(
            "QPushButton { background: #2a1a1a; border: 1px solid #663333; border-radius: 4px; }"
            "QPushButton:hover { background: #3a2020; border-color: #aa4444; }"
        )
        clear_btn.clicked.connect(self._clear_view)

        toolbar.addWidget(self.filter_edit, stretch=1)
        toolbar.addWidget(scroll_btn)
        toolbar.addWidget(clear_btn)
        layout.addLayout(toolbar)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a2a4a; max-height: 1px;")
        layout.addWidget(sep)

        # --- Zone de texte principale ---
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setFont(QFont("Consolas", 9))
        self.text_view.setStyleSheet(
            "QTextEdit { background: #121220; color: #d0d0e0; border: none; "
            "padding: 6px; selection-background-color: #3a3a6a; }"
        )
        layout.addWidget(self.text_view, stretch=1)

        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #2a2a4a; max-height: 1px;")
        layout.addWidget(sep2)

        # --- Barre de statut ---
        self.status_lbl = QLabel("⟳  Actualisation auto · 0 lignes")
        self.status_lbl.setStyleSheet("color: #666688; font-size: 8pt;")
        layout.addWidget(self.status_lbl)

    def _load_log(self):
        from engine import LOG_PATH
        if not LOG_PATH.exists():
            self._raw_lines = []
            self._last_size = 0
            self.text_view.setHtml(
                '<span style="color:#666688; font-style:italic;">Aucun log disponible.</span>'
            )
            return
        size = LOG_PATH.stat().st_size
        self._last_size = size
        try:
            text = LOG_PATH.read_text(encoding="utf-8", errors="replace")
            self._raw_lines = text.splitlines()
        except Exception:
            self._raw_lines = []
        self._apply_filter(self.filter_edit.text())

    def _refresh(self):
        if self._cleared:
            return
        from engine import LOG_PATH
        if not LOG_PATH.exists():
            return
        try:
            size = LOG_PATH.stat().st_size
        except Exception:
            return
        if size == self._last_size:
            return
        # Contenu a changé → recharger
        self._load_log()

    def _apply_filter(self, text: str):
        if self._cleared:
            return
        keyword = text.strip().lower()
        lines = self._raw_lines if not keyword else [
            l for l in self._raw_lines if keyword in l.lower()
        ]
        lines = list(reversed(lines))

        # Vérifier si on est en haut avant le rendu
        sb = self.text_view.verticalScrollBar()
        was_at_top = sb.value() <= 10

        html_lines = []
        for line in lines:
            escaped = (line
                       .replace("&", "&amp;")
                       .replace("<", "&lt;")
                       .replace(">", "&gt;"))
            color = "#d0d0e0"
            for lvl, c in self._LEVEL_COLORS.items():
                if lvl in line:
                    color = c
                    break
            html_lines.append(f'<span style="color:{color};">{escaped}</span>')

        self.text_view.setHtml(
            '<pre style="font-family:Consolas,monospace; font-size:9pt; '
            'line-height:1.4; white-space:pre-wrap; margin:0;">'
            + "<br>".join(html_lines)
            + "</pre>"
        )

        n = len(lines)
        self.status_lbl.setText(f"⟳  Actualisation auto · {n} ligne{'s' if n > 1 else ''}")

        # Auto-scroll seulement si on était déjà en haut
        if was_at_top:
            self._scroll_to_top()

    def _scroll_to_top(self):
        self.text_view.verticalScrollBar().setValue(0)

    def _clear_view(self):
        self._cleared = True
        self.text_view.clear()
        self.status_lbl.setText("Vue effacée · Cliquez sur ⟳ Scanner pour recharger")
        # Ajouter un bouton pour restaurer
        self.filter_edit.setPlaceholderText("Vue effacée — appuyez sur Entrée pour recharger")
        self.filter_edit.returnPressed.connect(self._restore_view)

    def _restore_view(self):
        self._cleared = False
        self.filter_edit.setPlaceholderText("🔍  Filtrer les lignes…")
        try:
            self.filter_edit.returnPressed.disconnect(self._restore_view)
        except Exception:
            pass
        self._load_log()

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Dialogue Paramètres
# ---------------------------------------------------------------------------
class SettingsDialog(QDialog):
    """Fenêtre de paramètres généraux."""

    update_signal = pyqtSignal(str)        # thread-safe status updates
    progress_signal = pyqtSignal(int, str) # progress bar updates
    done_signal = pyqtSignal(bool, str)    # download finished

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._asset_url = ""
        self.setWindowTitle("Paramètres — USB Detect")
        self.setMinimumWidth(460)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.update_signal.connect(self._set_update_status)
        self.progress_signal.connect(self._set_progress)
        self.done_signal.connect(self._on_download_done)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        title = QLabel("Paramètres")
        title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #c0c0ff;")
        layout.addWidget(title)

        chk_style = "QCheckBox { color: #d0d0e0; } QCheckBox::indicator { width: 16px; height: 16px; }"

        # --- Démarrage ---
        grp_start = QLabel("Démarrage")
        grp_start.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8888cc; margin-top: 6px;")
        layout.addWidget(grp_start)

        self.chk_startup = QCheckBox("Lancer USB Detect au démarrage de Windows")
        self.chk_startup.setChecked(self.config.start_with_windows)
        self.chk_startup.setStyleSheet(chk_style)
        layout.addWidget(self.chk_startup)

        self.chk_tray = QCheckBox("Démarrer en arrière-plan (system tray)")
        self.chk_tray.setChecked(self.config.start_in_tray)
        self.chk_tray.setStyleSheet(chk_style)
        layout.addWidget(self.chk_tray)

        self.chk_minimized = QCheckBox("Démarrer fenêtre minimisée")
        self.chk_minimized.setChecked(self.config.start_minimized)
        self.chk_minimized.setStyleSheet(chk_style)
        layout.addWidget(self.chk_minimized)

        # --- Notifications ---
        grp_notif = QLabel("Notifications")
        grp_notif.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8888cc; margin-top: 6px;")
        layout.addWidget(grp_notif)

        self.chk_notif = QCheckBox("Activer les notifications")
        self.chk_notif.setChecked(self.config.notifications_enabled)
        self.chk_notif.setStyleSheet(chk_style)
        layout.addWidget(self.chk_notif)

        self.chk_log = QCheckBox("Activer les logs")
        self.chk_log.setChecked(self.config.log_enabled)
        self.chk_log.setStyleSheet(chk_style)
        layout.addWidget(self.chk_log)

        # --- Configuration (import/export) ---
        grp_cfg = QLabel("Configuration")
        grp_cfg.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8888cc; margin-top: 6px;")
        layout.addWidget(grp_cfg)

        cfg_row = QHBoxLayout()
        cfg_row.setSpacing(8)
        cfg_info = QLabel("Sauvegardez vos macros avant une mise à jour")
        cfg_info.setStyleSheet("color: #8888aa; font-size: 8pt;")
        cfg_row.addWidget(cfg_info)
        cfg_row.addStretch()

        btn_style = (
            "QPushButton { background: #2a2a4a; border: 1px solid #44447a; border-radius: 4px; "
            "color: #a0a0e0; padding: 4px 12px; font-size: 9pt; }"
            "QPushButton:hover { background: #3a3a5a; }"
        )

        export_btn = QPushButton("Exporter")
        export_btn.setStyleSheet(btn_style)
        export_btn.clicked.connect(self._export_config)
        cfg_row.addWidget(export_btn)

        import_btn = QPushButton("Importer")
        import_btn.setStyleSheet(btn_style)
        import_btn.clicked.connect(self._import_config)
        cfg_row.addWidget(import_btn)

        layout.addLayout(cfg_row)

        # --- Mises à jour ---
        grp_update = QLabel("Mises à jour")
        grp_update.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8888cc; margin-top: 6px;")
        layout.addWidget(grp_update)

        update_row = QHBoxLayout()
        update_row.setSpacing(8)
        ver_lbl = QLabel(f"Version actuelle : v{APP_VERSION}")
        ver_lbl.setStyleSheet("color: #a0a0c0; font-size: 9pt;")
        update_row.addWidget(ver_lbl)
        update_row.addStretch()

        self.update_status_lbl = QLabel("")
        self.update_status_lbl.setStyleSheet("color: #66cc88; font-size: 9pt;")
        update_row.addWidget(self.update_status_lbl)

        self.check_update_btn = QPushButton("Vérifier")
        self.check_update_btn.setStyleSheet(btn_style)
        self.check_update_btn.clicked.connect(self._check_update)
        update_row.addWidget(self.check_update_btn)

        self.download_btn = QPushButton("Installer la mise à jour")
        self.download_btn.setStyleSheet(
            "QPushButton { background: #1a3a1a; border: 1px solid #2a6a2a; border-radius: 4px; "
            "color: #88ee88; padding: 4px 12px; font-size: 9pt; }"
            "QPushButton:hover { background: #2a5a2a; }"
            "QPushButton:disabled { background: #1a1a2a; color: #555577; border-color: #333355; }"
        )
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self._download_update)
        update_row.addWidget(self.download_btn)
        layout.addLayout(update_row)

        # Barre de progression (masquée par défaut)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background: #1a1a2a; border: 1px solid #333355; border-radius: 4px; "
            "height: 18px; text-align: center; color: #a0a0e0; font-size: 8pt; }"
            "QProgressBar::chunk { background: #2a5a2a; border-radius: 3px; }"
        )
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        # --- Boutons ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        save_btn = QPushButton("Sauvegarder")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    # ---- Import / Export config ----
    def _export_config(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter la configuration", "usb_detect_config.json",
            "JSON (*.json)")
        if path:
            import shutil
            try:
                shutil.copy2(str(CONFIG_PATH), path)
                QMessageBox.information(self, "Export", f"Configuration exportée vers :\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible d'exporter :\n{e}")

    def _import_config(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer une configuration", "",
            "JSON (*.json)")
        if not path:
            return
        try:
            import json as _json
            with open(path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            # Validation minimale
            if "devices" not in data or "general" not in data:
                QMessageBox.warning(self, "Erreur",
                    "Ce fichier n'est pas une configuration USB Detect valide.")
                return
            import shutil
            shutil.copy2(path, str(CONFIG_PATH))
            QMessageBox.information(self, "Import",
                "Configuration importée avec succès.\n"
                "Redémarrez USB Detect pour appliquer les changements.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible d'importer :\n{e}")

    # ---- Mise à jour ----
    def _check_update(self):
        self.check_update_btn.setEnabled(False)
        self.update_status_lbl.setText("Vérification…")
        self.update_status_lbl.setStyleSheet("color: #8888cc; font-size: 9pt;")

        def _on_result(version, url, asset_url):
            if version:
                self._asset_url = asset_url or ""
                self.update_signal.emit(f"v{version} disponible !")
                if asset_url:
                    self.download_btn.setVisible(True)
                parent = self.parent()
                if parent and hasattr(parent, "update_available"):
                    parent.update_available.emit(version, url)
            else:
                self.update_signal.emit("Vous êtes à jour.")
            self.check_update_btn.setEnabled(True)

        check_for_update(_on_result)

    def _set_update_status(self, text):
        self.update_status_lbl.setText(text)
        self.update_status_lbl.setStyleSheet("color: #66cc88; font-size: 9pt;")

    def _download_update(self):
        if not self._asset_url:
            QMessageBox.warning(self, "Erreur", "Aucun fichier de mise à jour trouvé dans la release.")
            return
        self.download_btn.setEnabled(False)
        self.check_update_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Connexion…")

        def _progress(pct, status):
            self.progress_signal.emit(pct, status)

        def _done(success, info):
            self.done_signal.emit(success, info)

        download_and_apply_update(self._asset_url, _progress, _done)

    def _set_progress(self, pct, status):
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(status)

    def _on_download_done(self, success, info):
        if success:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Prêt ! Redémarrage…")
            bat_path = info
            reply = QMessageBox.question(
                self, "Mise à jour prête",
                "La mise à jour a été téléchargée.\n\n"
                "USB Detect va se fermer et se relancer automatiquement.\n"
                "Votre configuration sera conservée.\n\n"
                "Continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                import subprocess as _sp
                _sp.Popen(["cmd", "/c", bat_path],
                          creationflags=0x08000000)  # CREATE_NO_WINDOW
                QApplication.quit()
            else:
                self.progress_bar.setFormat("Mise à jour en attente")
                self.download_btn.setEnabled(True)
        else:
            self.progress_bar.setVisible(False)
            self.download_btn.setEnabled(True)
            self.check_update_btn.setEnabled(True)
            QMessageBox.warning(self, "Erreur de mise à jour", f"Le téléchargement a échoué :\n{info}")

    def _save(self):
        self.config.start_with_windows = self.chk_startup.isChecked()
        self.config.start_in_tray = self.chk_tray.isChecked()
        self.config.start_minimized = self.chk_minimized.isChecked()
        self.config.notifications_enabled = self.chk_notif.isChecked()
        self.config.log_enabled = self.chk_log.isChecked()
        self.config.save()

        set_startup_enabled(self.config.start_with_windows)

        self.accept()


# ---------------------------------------------------------------------------
# Thread de scan périodique (toutes les 2s)
# ---------------------------------------------------------------------------
class ScanWorker(QThread):
    scan_done = pyqtSignal()

    def __init__(self, engine: Engine):
        super().__init__()
        self.engine = engine
        self._first = True
        self._running = True

    def run(self):
        import time
        while self._running:
            self.engine.scan_and_update(first_run=self._first)
            self._first = False
            self.scan_done.emit()
            time.sleep(5)  # Scan toutes les 5 secondes via WMI natif (pas de PowerShell)

    def stop(self):
        self._running = False
        self.wait()


# ---------------------------------------------------------------------------
# Carte d'un périphérique dans la liste
# ---------------------------------------------------------------------------
class DeviceCard(QWidget):
    edit_requested = pyqtSignal(object)             # Device
    delete_requested = pyqtSignal(object)           # Device
    test_connect_requested = pyqtSignal(object)     # Device
    test_disconnect_requested = pyqtSignal(object)  # Device
    toggle_requested = pyqtSignal(object)           # Device (enable/disable)

    def __init__(self, device: Device, parent=None):
        super().__init__(parent)
        self.device = device
        self.setObjectName("DeviceCard")
        self.setStyleSheet("""
            #DeviceCard {
                background: #2a2a3e;
                border: 1px solid #3a3a4a;
                border-radius: 8px;
            }
            #DeviceCard:hover { border-color: #5050aa; }
        """)
        self._build()

    def _build(self):
        from PyQt6.QtWidgets import QSizePolicy as _SP
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # --- Indicateur de statut (cercle coloré) ---
        self.dot = QLabel("⬤")
        self.dot.setFixedWidth(20)
        self.dot.setFont(QFont("Segoe UI", 13))
        self.dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dot.setToolTip("Statut de connexion du périphérique")

        # --- Icône selon le type de périphérique ---
        dev_type = get_device_type(self.device.id, self.device.name)
        icon_fn = _DEVICE_ICONS.get(dev_type, icon_usb)
        dev_icon_lbl = QLabel()
        dev_icon_lbl.setPixmap(icon_fn().pixmap(18, 18))
        dev_icon_lbl.setFixedSize(20, 20)
        dev_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _type_labels = {
            "monitor": "Moniteur HDMI/DisplayPort", "keyboard": "Clavier",
            "mouse": "Souris", "hub": "Hub USB", "audio": "Audio",
            "gamepad": "Manette", "hid": "Périphérique HID", "usb": "Périphérique USB",
        }
        dev_icon_lbl.setToolTip(_type_labels.get(dev_type, "Périphérique"))
        usb_icon_lbl = dev_icon_lbl  # alias pour le reste du code

        # --- Bloc info (nom + ID + compteur d'actions) ---
        info = QVBoxLayout()
        info.setSpacing(2)

        self.name_lbl = QLabel(self.device.name)
        self.name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.name_lbl.setMinimumWidth(0)
        self.name_lbl.setSizePolicy(_SP.Policy.Expanding, _SP.Policy.Preferred)

        n_con = len(self.device.on_connect)
        n_dis = len(self.device.on_disconnect)
        match_labels = {"contains": "contient", "exact": "exact", "regex": "regex"}
        match_txt = match_labels.get(self.device.match_type, self.device.match_type)

        # ID tronqué en monospace — tooltip affiche la valeur complète
        _id_full = self.device.id
        _id_disp = (_id_full[:42] + "…") if len(_id_full) > 44 else _id_full
        self.id_lbl = QLabel(f"ID : {_id_disp}")
        self.id_lbl.setFont(QFont("Consolas", 8))
        self.id_lbl.setStyleSheet("color: #666688;")
        self.id_lbl.setToolTip(f"Identifiant complet :\n{_id_full}")
        self.id_lbl.setMinimumWidth(0)
        self.id_lbl.setSizePolicy(_SP.Policy.Ignored, _SP.Policy.Preferred)

        # Compteurs d'actions en HTML coloré
        self.actions_lbl = QLabel()
        self.actions_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.actions_lbl.setWordWrap(True)
        self.actions_lbl.setMinimumWidth(0)
        self.actions_lbl.setSizePolicy(_SP.Policy.Expanding, _SP.Policy.Preferred)
        _lbl_con = "connexion" if n_con <= 1 else "connexions"
        _lbl_dis = "déconnexion" if n_dis <= 1 else "déconnexions"
        self.actions_lbl.setText(
            f'<span style="color:#00aa55; font-weight:600;">⚡ {n_con}</span>'
            f'<span style="color:#3a7a55;"> {_lbl_con} &nbsp;</span>'
            f'<span style="color:#aa3333; font-weight:600;">✖ {n_dis}</span>'
            f'<span style="color:#7a3a3a;"> {_lbl_dis} &nbsp;·&nbsp; </span>'
            f'<span style="color:#444466;">{match_txt}</span>'
        )
        self.actions_lbl.setStyleSheet("font-size: 8pt;")

        info.addWidget(self.name_lbl)
        info.addWidget(self.id_lbl)
        info.addWidget(self.actions_lbl)

        # --- Badge de statut ---
        self.state_lbl = QLabel("…")
        self.state_lbl.setFixedWidth(100)
        self.state_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.state_lbl.setStyleSheet("font-size: 8pt; border-radius: 4px; padding: 3px 6px;")

        # --- Boutons de test d'actions ---
        test_con_btn = QPushButton("⚡")
        test_con_btn.setFixedSize(30, 30)
        n_con_actions = len(self.device.on_connect)
        test_con_btn.setToolTip(
            f"Simuler une CONNEXION\n"
            f"{n_con_actions} action{'s' if n_con_actions > 1 else ''} à exécuter\n"
            "(fonctionne sans brancher le périphérique)"
        )
        test_con_btn.setStyleSheet("""
            QPushButton {
                background: #163016; border: 1px solid #2a6a2a;
                border-radius: 6px; color: #44cc44; font-size: 12pt; font-weight: bold;
            }
            QPushButton:hover   { background: #1e4a1e; border-color: #44aa44; }
            QPushButton:pressed { background: #2a7a2a; }
            QPushButton:disabled { color: #335533; border-color: #1a3a1a; background: #111e11; }
        """)
        test_con_btn.setEnabled(bool(self.device.on_connect))
        test_con_btn.clicked.connect(lambda: self.test_connect_requested.emit(self.device))

        test_dis_btn = QPushButton("⏏")
        test_dis_btn.setFixedSize(30, 30)
        n_dis_actions = len(self.device.on_disconnect)
        test_dis_btn.setToolTip(
            f"Simuler une DÉCONNEXION\n"
            f"{n_dis_actions} action{'s' if n_dis_actions > 1 else ''} à exécuter\n"
            "(fonctionne sans débrancher le périphérique)"
        )
        test_dis_btn.setStyleSheet("""
            QPushButton {
                background: #2a1a08; border: 1px solid #7a4a10;
                border-radius: 6px; color: #ee9933; font-size: 11pt; font-weight: bold;
            }
            QPushButton:hover   { background: #3e2510; border-color: #cc8822; }
            QPushButton:pressed { background: #5a3210; }
            QPushButton:disabled { color: #554433; border-color: #3a2a10; background: #1e1208; }
        """)
        test_dis_btn.setEnabled(bool(self.device.on_disconnect))
        test_dis_btn.clicked.connect(lambda: self.test_disconnect_requested.emit(self.device))

        # Petit séparateur vertical entre les groupes de boutons
        from PyQt6.QtWidgets import QFrame
        sep_v = QFrame()
        sep_v.setFrameShape(QFrame.Shape.VLine)
        sep_v.setStyleSheet("color: #3a3a4a; max-width: 1px;")
        sep_v.setFixedHeight(24)

        # --- Bouton ON/OFF (toggle enabled) ---
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setToolTip("Activer / Désactiver ce macro")
        self.toggle_btn.clicked.connect(lambda: self.toggle_requested.emit(self.device))
        self._update_toggle_style()

        # --- Boutons d'action ---
        edit_btn = QPushButton()
        edit_btn.setIcon(icon_edit())
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Modifier la configuration de ce périphérique")
        edit_btn.setStyleSheet("""
            QPushButton { background: #2a2a4a; border: 1px solid #4040aa; border-radius: 6px; }
            QPushButton:hover { background: #3a3a6a; border-color: #6060cc; }
            QPushButton:pressed { background: #5050aa; }
        """)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.device))

        del_btn = QPushButton()
        del_btn.setIcon(icon_delete())
        del_btn.setIconSize(QSize(16, 16))
        del_btn.setFixedSize(32, 32)
        del_btn.setToolTip("Supprimer définitivement ce périphérique et ses actions")
        del_btn.setStyleSheet("""
            QPushButton { background: #3a1a1a; border: 1px solid #aa3333; border-radius: 6px; }
            QPushButton:hover { background: #4a2020; border-color: #dd4444; }
            QPushButton:pressed { background: #6a2020; }
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.device))

        layout.addWidget(self.dot)
        layout.addWidget(usb_icon_lbl)
        layout.addLayout(info, stretch=1)
        layout.addWidget(self.state_lbl)
        layout.addWidget(test_con_btn)
        layout.addWidget(test_dis_btn)
        layout.addWidget(sep_v)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)

        # Opacité si désactivé
        if not self.device.enabled:
            self.setStyleSheet(self.styleSheet() + "\n#DeviceCard { opacity: 0.5; }")

        # Tooltip global sur la carte
        status_txt = "Activé" if self.device.enabled else "Désactivé"
        self.setToolTip(
            f"Type : {_type_labels.get(dev_type, 'Périphérique')}\n"
            f"Nom : {self.device.name}\n"
            f"Identifiant : {self.device.id}\n"
            f"Correspondance : {self.device.match_type}\n"
            f"Statut : {status_txt}"
        )

    def _update_toggle_style(self):
        if self.device.enabled:
            self.toggle_btn.setText("ON")
            self.toggle_btn.setStyleSheet("""
                QPushButton { background: #1a3a1a; border: 1px solid #2a8a2a; border-radius: 6px;
                              color: #44cc44; font-size: 8pt; font-weight: bold; }
                QPushButton:hover { background: #2a5a2a; border-color: #44aa44; }
            """)
        else:
            self.toggle_btn.setText("OFF")
            self.toggle_btn.setStyleSheet("""
                QPushButton { background: #2a1a1a; border: 1px solid #6a3333; border-radius: 6px;
                              color: #aa5555; font-size: 8pt; font-weight: bold; }
                QPushButton:hover { background: #3a2020; border-color: #aa4444; }
            """)

    def update_state(self, connected: bool):
        if not self.device.enabled:
            self.dot.setStyleSheet("color: #444455;")
            self.state_lbl.setText("DÉSACTIVÉ")
            self.state_lbl.setStyleSheet(
                "color: #555566; background: rgba(80,80,100,0.10); "
                "border-radius: 4px; padding: 3px 6px; font-size: 8pt; font-weight: bold;"
            )
            self.name_lbl.setStyleSheet("color: #666688;")
            return
        self.name_lbl.setStyleSheet("")
        if connected:
            self.dot.setStyleSheet("color: #00dd77;")
            self.state_lbl.setText("CONNECTÉ")
            self.state_lbl.setStyleSheet(
                "color: #00dd77; background: rgba(0,220,120,0.14); "
                "border-radius: 4px; padding: 3px 6px; font-size: 8pt; font-weight: bold;"
            )
        else:
            self.dot.setStyleSheet("color: #666688;")
            self.state_lbl.setText("DÉCONNECTÉ")
            self.state_lbl.setStyleSheet(
                "color: #777799; background: rgba(100,100,150,0.10); "
                "border-radius: 4px; padding: 3px 6px; font-size: 8pt; font-weight: bold;"
            )


# ---------------------------------------------------------------------------
# Fenêtre principale
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    confirm_signal = pyqtSignal(object, bool)  # (device, confirmed)
    update_available = pyqtSignal(str, str)     # (version, url)

    def __init__(self, engine: Engine):
        super().__init__()
        self.engine = engine
        self.config = engine.config
        self.cards: dict[str, DeviceCard] = {}  # device.name → card
        self._update_url: str = ""

        self.setWindowTitle(f"USB Detect v{APP_VERSION}")
        self.setMinimumSize(660, 400)
        self.setWindowFlags(Qt.WindowType.Window)
        self._log_viewer: LogViewer | None = None

        # Icône de fenêtre : priorité au fichier .ico, sinon icône USB générée via SVG
        ico_path = BASE_DIR / "usb_detect.ico"
        if ico_path.exists():
            self.setWindowIcon(QIcon(str(ico_path)))
        else:
            self.setWindowIcon(_make_window_icon())

        self._build_ui()
        self._build_tray()
        self._build_worker()
        self.resize(780, 520)

        # Connecter les callbacks engine → UI
        self.engine.on_device_changed = self._on_device_changed
        self.engine.on_confirm_needed = self._ask_confirm
        self.engine.on_notify = self._notify

        # Vérification des mises à jour au lancement
        self.update_available.connect(self._show_update_banner)
        check_for_update(self._on_update_result)

        # Démarrage : masquer si start_in_tray ou start_minimized
        if self.config.start_in_tray or self.config.start_minimized:
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            QTimer.singleShot(0, self.hide)
        else:
            self.show()

    # ---- Construction UI ----
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        # ── Bannière de mise à jour (masquée par défaut) ─────────────────────
        self.update_banner = QWidget()
        self.update_banner.setStyleSheet(
            "background: #1a2a1a; border: 1px solid #2a6a2a; border-radius: 6px;"
        )
        self.update_banner.setVisible(False)
        ub_lay = QHBoxLayout(self.update_banner)
        ub_lay.setContentsMargins(10, 6, 10, 6)
        ub_lay.setSpacing(8)
        self.update_lbl = QLabel("")
        self.update_lbl.setStyleSheet(
            "color: #66cc88; font-size: 9pt; background: transparent; border: none;"
        )
        update_btn = QPushButton("Mettre à jour")
        update_btn.setStyleSheet(
            "QPushButton { background: #2a5a2a; border: 1px solid #44aa44; border-radius: 4px; "
            "color: #88ee88; padding: 3px 10px; font-size: 9pt; }"
            "QPushButton:hover { background: #3a7a3a; }"
        )
        update_btn.clicked.connect(self._open_update_url)
        dismiss_btn = QPushButton("X")
        dismiss_btn.setFixedSize(22, 22)
        dismiss_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #558855; font-size: 10pt; }"
            "QPushButton:hover { color: #88cc88; }"
        )
        dismiss_btn.clicked.connect(lambda: self.update_banner.setVisible(False))
        ub_lay.addWidget(self.update_lbl, stretch=1)
        ub_lay.addWidget(update_btn)
        ub_lay.addWidget(dismiss_btn)
        root.addWidget(self.update_banner)

        # ── En-tête compact ──────────────────────────────────────────────────
        hdr = QWidget()
        hdr.setStyleSheet(
            "background: #23233a; border-radius: 8px; border: 1px solid #30305a;"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 8, 14, 8)
        hdr_lay.setSpacing(10)

        title_lbl = QLabel(f"USB Detect  v{APP_VERSION}")
        title_lbl.setStyleSheet(
            "font-size: 12pt; font-weight: bold; color: #c0c0ff; "
            "background: transparent; border: none;"
        )
        self.summary_lbl = QLabel("Initialisation…")
        self.summary_lbl.setStyleSheet(
            "color: #555577; font-size: 9pt; background: transparent; border: none;"
        )
        hdr_lay.addWidget(title_lbl)
        hdr_lay.addStretch()
        hdr_lay.addWidget(self.summary_lbl)
        root.addWidget(hdr)

        # ── Zone des cartes dans un scroll area ──────────────────────────────
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_layout.setContentsMargins(0, 0, 4, 0)

        self._cards_scroll = QScrollArea()
        self._cards_scroll.setWidget(self.cards_container)
        self._cards_scroll.setWidgetResizable(True)
        self._cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._cards_scroll.setMinimumHeight(120)
        self._cards_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical { background: #1a1a2a; width: 6px; border-radius: 3px; }"
            "QScrollBar::handle:vertical { background: #3a3a6a; border-radius: 3px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        root.addWidget(self._cards_scroll, stretch=1)

        self._rebuild_cards()

        # ── Séparateur ────────────────────────────────────────────────────────
        from PyQt6.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #2a2a4a; background: #2a2a4a; max-height: 1px;")
        root.addWidget(sep)

        # ── Barre du bas ─────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        add_btn = QPushButton("＋  Ajouter un périphérique")
        add_btn.setObjectName("primary")
        add_btn.setToolTip("Configurer un nouveau périphérique USB et ses actions automatiques")
        add_btn.clicked.connect(self._add_device)

        self.scan_lbl = QLabel("⟳  Initialisation…")
        self.scan_lbl.setStyleSheet("color: #6666cc; font-size: 9pt;")
        self.scan_lbl.setToolTip("Scan automatique toutes les 5 secondes via WMI")

        settings_btn = QPushButton("Paramètres")
        settings_btn.setToolTip("Ouvrir les paramètres de l'application")
        settings_btn.clicked.connect(self._open_settings)

        log_btn = QPushButton("Logs")
        log_btn.setToolTip("Ouvrir la visionneuse de logs intégrée")
        log_btn.clicked.connect(self._open_log)

        btn_row.addWidget(add_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.scan_lbl)
        btn_row.addWidget(settings_btn)
        btn_row.addWidget(log_btn)
        root.addLayout(btn_row)

    def _fit_to_content(self):
        """Garantit la largeur minimale — le scroll area gère la hauteur."""
        if self.width() < 560:
            self.resize(560, self.height())

    def _rebuild_cards(self):
        # Vider
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cards.clear()

        for device in self.config.devices:
            card = DeviceCard(device)
            card.edit_requested.connect(self._edit_device)
            card.delete_requested.connect(self._delete_device)
            card.test_connect_requested.connect(self._test_connect)
            card.test_disconnect_requested.connect(self._test_disconnect)
            card.toggle_requested.connect(self._toggle_device)
            card.update_state(device.connected)
            self.cards[device.name] = card
            self.cards_layout.addWidget(card)

        if not self.config.devices:
            empty = QWidget()
            empty_layout = QVBoxLayout(empty)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setSpacing(10)
            empty_layout.setContentsMargins(20, 30, 20, 30)

            icon_lbl = QLabel("🔌")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("font-size: 36pt;")

            text_lbl = QLabel("Aucun périphérique configuré")
            text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_lbl.setStyleSheet("color: #8888aa; font-size: 11pt; font-weight: bold;")

            hint_lbl = QLabel(
                "Cliquez sur  ＋ Ajouter un périphérique  pour commencer.\n"
                "Chaque périphérique peut déclencher des actions\n"
                "automatiques à la connexion ou déconnexion USB."
            )
            hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_lbl.setStyleSheet("color: #555577; font-size: 9pt; line-height: 150%;")
            hint_lbl.setWordWrap(True)

            empty_layout.addWidget(icon_lbl)
            empty_layout.addWidget(text_lbl)
            empty_layout.addWidget(hint_lbl)
            self.cards_layout.addWidget(empty)

        self._update_summary()

    # ---- Systray ----
    def _build_tray(self):
        self.tray = QSystemTrayIcon(make_tray_icon(False), self)
        self._update_tray_tooltip()

        menu = QMenu()
        menu.setStyleSheet(STYLESHEET)

        show_action = QAction("Afficher", self)
        show_action.triggered.connect(self._show_window)
        add_action = QAction("Ajouter un périphérique", self)
        add_action.triggered.connect(self._add_device)
        settings_action = QAction("Paramètres", self)
        settings_action.triggered.connect(self._open_settings)
        reload_action = QAction("Recharger la config", self)
        reload_action.triggered.connect(self._reload_config)
        log_action = QAction("Ouvrir les logs", self)
        log_action.triggered.connect(self._open_log)
        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self._quit)

        menu.addAction(show_action)
        menu.addAction(add_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addAction(reload_action)
        menu.addAction(log_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _update_tray_tooltip(self):
        connected = [d.name for d in self.config.devices if d.connected]
        n_total = len(self.config.devices)
        n_con = len(connected)
        if n_con == 0:
            tip = f"USB Detect — {n_total} périphérique(s), aucun connecté"
        else:
            names = ", ".join(connected[:3])
            suffix = f" (+{n_con - 3})" if n_con > 3 else ""
            tip = f"USB Detect — {n_con}/{n_total} connecté(s)\n{names}{suffix}"
        self.tray.setToolTip(tip)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.setWindowState(
            self.windowState() & ~Qt.WindowState.WindowMinimized
        )
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ---- Worker de scan ----
    def _build_worker(self):
        self.worker = ScanWorker(self.engine)
        self.worker.scan_done.connect(self._on_scan_done)
        self.worker.start()

    def _update_summary(self):
        """Met à jour le résumé de l'en-tête (nombre de périphériques / connectés)."""
        n = len(self.config.devices)
        n_con = sum(1 for d in self.config.devices if d.connected)
        if n == 0:
            txt, color = "Aucun périphérique configuré", "#444466"
        elif n_con == 0:
            txt = f"{n} périphérique{'s' if n > 1 else ''}  ·  aucun connecté"
            color = "#555577"
        else:
            txt = f"{n} périphérique{'s' if n > 1 else ''}  ·  {n_con} connecté{'s' if n_con > 1 else ''}"
            color = "#44aa77"
        self.summary_lbl.setText(txt)
        self.summary_lbl.setStyleSheet(
            f"color: {color}; font-size: 9pt; background: transparent; border: none;"
        )

    def _on_scan_done(self):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        self.scan_lbl.setText(f"⟳  Dernier scan : {now}")
        self.scan_lbl.setStyleSheet("color: #44aa88; font-size: 9pt;")

        any_connected = any(d.connected for d in self.config.devices)
        self.tray.setIcon(make_tray_icon(any_connected))
        self._update_tray_tooltip()
        self._update_summary()

        for device in self.config.devices:
            if device.name in self.cards:
                self.cards[device.name].update_state(device.connected)

    # ---- Callbacks engine ----
    def _on_device_changed(self, device: Device):
        # Appelé depuis le thread worker → utiliser QTimer pour être thread-safe
        QTimer.singleShot(0, lambda: self._refresh_card(device))

    def _refresh_card(self, device: Device):
        if device.name in self.cards:
            self.cards[device.name].update_state(device.connected)

    def _ask_confirm(self, device: Device) -> bool:
        reply = QMessageBox.question(
            None,
            "USB Detect",
            f"{device.name} a été déconnecté.\n\nFermer les applications associées ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _notify(self, title: str, text: str):
        if self.tray.isVisible():
            self.tray.showMessage(
                title, text,
                QSystemTrayIcon.MessageIcon.Information,
                self.config.notification_duration * 1000,
            )

    # ---- Actions CRUD périphériques ----
    def _add_device(self):
        dlg = DeviceWizard(self.config, parent=self)
        dlg.setStyleSheet(STYLESHEET)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_device:
            self.config.devices.append(dlg.result_device)
            self.config.save()
            self._rebuild_cards()
            log.info(f"Périphérique ajouté : {dlg.result_device.name}")
            self._notify("Périphérique ajouté", f"{dlg.result_device.name} configuré.")

    def _edit_device(self, device: Device):
        dlg = DeviceWizard(self.config, device=device, parent=self)
        dlg.setStyleSheet(STYLESHEET)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.config.save()
            self._rebuild_cards()
            log.info(f"Périphérique modifié : {device.name}")

    def _delete_device(self, device: Device):
        reply = QMessageBox.question(
            self, "Supprimer",
            f"Supprimer « {device.name} » et toutes ses actions ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.devices.remove(device)
            self.config.save()
            self._rebuild_cards()
            log.info(f"Périphérique supprimé : {device.name}")

    def _toggle_device(self, device: Device):
        """Active ou désactive un macro sans le supprimer."""
        device.enabled = not device.enabled
        self.config.save()
        self._rebuild_cards()
        state = "activé" if device.enabled else "désactivé"
        log.info(f"Macro {state} : {device.name}")
        self._notify("USB Detect", f"{device.name} {state}")

    def _test_connect(self, device: Device):
        """Déclenche manuellement les actions de connexion, indépendamment de l'état réel."""
        import threading
        log.info(f"[TEST] Actions de connexion pour : {device.name}")
        self._notify("Test", f"Simulation connexion : {device.name}")
        threading.Thread(
            target=self.engine._execute_actions,
            args=(device, device.on_connect),
            daemon=True,
        ).start()

    def _test_disconnect(self, device: Device):
        """Déclenche manuellement les actions de déconnexion, indépendamment de l'état réel."""
        import threading
        log.info(f"[TEST] Actions de déconnexion pour : {device.name}")
        self._notify("Test", f"Simulation déconnexion : {device.name}")
        threading.Thread(
            target=self.engine._execute_actions,
            args=(device, device.on_disconnect),
            daemon=True,
        ).start()

    def _reload_config(self):
        """Recharge la config depuis le disque sans redémarrer l'appli."""
        from engine import Config
        self.engine.config = Config.load()
        self.config = self.engine.config
        self._rebuild_cards()
        self._update_tray_tooltip()
        log.info("Configuration rechargée.")
        self._notify("USB Detect", "Configuration rechargée.")

    def _open_log(self):
        if self._log_viewer and self._log_viewer.isVisible():
            self._log_viewer.raise_()
            self._log_viewer.activateWindow()
            return
        self._log_viewer = LogViewer(parent=self)
        self._log_viewer.setStyleSheet(STYLESHEET)
        self._log_viewer.show()

    def _open_settings(self):
        dlg = SettingsDialog(self.config, parent=self)
        dlg.setStyleSheet(STYLESHEET)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            log.info("Paramètres sauvegardés.")
            self._notify("USB Detect", "Paramètres sauvegardés.")

    # ---- Mise à jour GitHub ----
    def _on_update_result(self, version, url, asset_url=None):
        """Callback appelé depuis un thread — émet un signal pour l'UI."""
        if version:
            self.update_available.emit(version, url)

    def _show_update_banner(self, version: str, url: str):
        """Affiche la bannière de mise à jour dans l'UI."""
        self._update_url = url
        self.update_lbl.setText(f"Nouvelle version disponible : v{version}")
        self.update_banner.setVisible(True)

    def _open_update_url(self):
        if self._update_url:
            webbrowser.open(self._update_url)

    def _quit(self):
        self.worker.stop()
        QApplication.quit()

    def closeEvent(self, event):
        # Fermer la fenêtre → minimiser dans le systray (sans popup répétitif)
        event.ignore()
        self.hide()
        if not getattr(self, "_close_notified", False):
            self._close_notified = True
            self.tray.showMessage(
                "USB Detect", "Toujours actif dans la barre des tâches.",
                QSystemTrayIcon.MessageIcon.Information, 2000,
            )


# ---------------------------------------------------------------------------
# Auto-installation / mise à jour
# ---------------------------------------------------------------------------
def _handle_install_or_update():
    """Gère l'installation ou la mise à jour au premier lancement du .exe."""
    import ctypes

    if not getattr(sys, "frozen", False):
        return  # Mode dev → on lance directement

    # Argument --install : appelé après élévation UAC
    if "--install" in sys.argv:
        self_install(is_update=False)
        dest = str(INSTALL_DIR / "USB Detect.exe")
        import subprocess as _sp
        _sp.Popen([dest], creationflags=0x00000008)  # DETACHED_PROCESS
        sys.exit(0)

    # Argument --update : appelé après élévation UAC
    if "--update" in sys.argv:
        self_install(is_update=True)
        dest = str(INSTALL_DIR / "USB Detect.exe")
        import subprocess as _sp
        _sp.Popen([dest], creationflags=0x00000008)
        sys.exit(0)

    # Argument --uninstall
    if "--uninstall" in sys.argv:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, '"--uninstall"', None, 1)
            sys.exit(0)
        app = QApplication(sys.argv)
        app.setStyleSheet(STYLESHEET)
        reply = QMessageBox.question(
            None, "USB Detect — Désinstallation",
            "Voulez-vous désinstaller USB Detect ?\n\n"
            "Votre configuration (macros) sera sauvegardée sur le bureau.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self_uninstall()
            QMessageBox.information(None, "Désinstallation terminée",
                "USB Detect a été désinstallé.\n"
                "Votre config a été sauvegardée sur le bureau.")
        sys.exit(0)

    # Vérifier le statut d'installation
    status = check_install_status()

    if status == "run":
        return  # Déjà installé ou même version → lancement normal

    if status == "older":
        # Version plus ancienne que celle installée → lancer l'installée
        dest = str(INSTALL_DIR / "USB Detect.exe")
        if Path(dest).exists():
            import subprocess as _sp
            _sp.Popen([dest], creationflags=0x00000008)
        sys.exit(0)

    # Première installation ou mise à jour
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    if status == "install":
        reply = QMessageBox.question(
            None, "USB Detect — Installation",
            f"Bienvenue ! USB Detect va s'installer dans :\n"
            f"{INSTALL_DIR}\n\n"
            f"Un raccourci sera créé dans le menu Démarrer\n"
            f"et l'application apparaîtra dans vos programmes.\n\n"
            f"Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        flag = "--install"
    else:  # status == "update"
        old_ver = get_installed_version() or "?"
        reply = QMessageBox.question(
            None, "USB Detect — Mise à jour",
            f"Une version plus récente va être installée :\n\n"
            f"  Version installée : v{old_ver}\n"
            f"  Nouvelle version  : v{APP_VERSION}\n\n"
            f"Votre configuration (macros) sera conservée.\n\n"
            f"Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        flag = "--update"

    if reply != QMessageBox.StandardButton.Yes:
        sys.exit(0)

    # Demander élévation admin si nécessaire
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{flag}"', None, 1)
        sys.exit(0)

    # On a déjà les droits admin
    self_install(is_update=(status == "update"))
    dest = str(INSTALL_DIR / "USB Detect.exe")
    import subprocess as _sp
    _sp.Popen([dest], creationflags=0x00000008)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
def main():
    # Auto-installation / mise à jour / désinstallation
    _handle_install_or_update()

    # Vérifier instance unique via fichier lock (avec vérification du PID)
    lock_path = BASE_DIR / "usb_detect.lock"
    if lock_path.exists():
        try:
            pid = int(lock_path.read_text().strip())
            import psutil
            if psutil.pid_exists(pid):
                app = QApplication(sys.argv)
                QMessageBox.warning(None, "USB Detect", "Une instance est déjà en cours d'exécution.")
                sys.exit(1)
            else:
                lock_path.unlink()
        except Exception:
            lock_path.unlink(missing_ok=True)

    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("USBDetect.App.v2")
    except Exception:
        pass

    lock_path.write_text(str(os.getpid()))
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("USB Detect")
        app.setQuitOnLastWindowClosed(False)
        app.setStyleSheet(STYLESHEET)

        config = Config.load()
        engine = Engine(config)
        engine.apply_taskbar()

        window = MainWindow(engine)

        sys.exit(app.exec())
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
