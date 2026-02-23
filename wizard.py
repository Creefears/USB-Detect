"""
USB Detect v2 - Wizard d'ajout/édition de périphérique
"""

from PyQt6.QtCore import QByteArray, QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton,
    QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
    QDoubleSpinBox,
)

from engine import Action, Config, Device, get_device_type, is_internal_device, scan_usb_list


# ---------------------------------------------------------------------------
# Icônes SVG locales au wizard
# ---------------------------------------------------------------------------
def _make_svg_icon(svg: str, size: int = 16) -> QIcon:
    from PyQt6.QtSvg import QSvgRenderer
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)


def _icon_remove() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="#dd4444" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
        <path d="M10 11v6M14 11v6"/>
        <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
    </svg>'''
    return _make_svg_icon(svg)


def _icon_browse() -> QIcon:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="#aaaaff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        <line x1="12" y1="11" x2="12" y2="17"/>
        <line x1="9" y1="14" x2="15" y2="14"/>
    </svg>'''
    return _make_svg_icon(svg)


def _icon_settings() -> QIcon:
    """Engrenage — bouton Options avancées."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="#aaaaff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06
                 a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09
                 A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83
                 l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09
                 A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83
                 l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09
                 a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83
                 l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09
                 a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>'''
    return _make_svg_icon(svg, 14)

_DEVICE_SVGS = {
    "monitor":  '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>''',
    "keyboard": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><rect x="2" y="6" width="20" height="13" rx="2"/><line x1="6" y1="10" x2="6.01" y2="10"/><line x1="10" y1="10" x2="10.01" y2="10"/><line x1="14" y1="10" x2="14.01" y2="10"/><line x1="18" y1="10" x2="18.01" y2="10"/><line x1="6" y1="14" x2="18" y2="14"/></svg>''',
    "mouse":    '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><path d="M6 10a6 6 0 0 1 12 0v5a6 6 0 0 1-12 0v-5z"/><line x1="12" y1="4" x2="12" y2="11"/><line x1="6" y1="10.5" x2="18" y2="10.5"/></svg>''',
    "hub":      '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><line x1="12" y1="9" x2="12" y2="3"/><line x1="14.6" y1="13.5" x2="20" y2="17"/><line x1="9.4" y1="13.5" x2="4" y2="17"/></svg>''',
    "audio":    '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>''',
    "storage":  '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 5v14c0 1.66-4.03 3-9 3S3 20.66 3 19V5"/><path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3"/></svg>''',
    "gamepad":  '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="11" x2="15.01" y2="11"/><line x1="18" y1="13" x2="18.01" y2="13"/><path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59l-.9 7.9A4 4 0 0 0 5.78 21a4 4 0 0 0 3.58-2.21L10 17h4l.64 1.79A4 4 0 0 0 18.22 21a4 4 0 0 0 3.978-4.51l-.9-7.9A4 4 0 0 0 17.32 5z"/></svg>''',
    "hid":      '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/><line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/></svg>''',
    "usb":      '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8888cc" stroke-width="2" stroke-linecap="round"><path d="M12 2v12"/><path d="M8 6l4-4 4 4"/><path d="M6 15h12a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2z"/></svg>''',
}


def _device_icon(device_type: str) -> QIcon:
    svg = _DEVICE_SVGS.get(device_type, _DEVICE_SVGS["usb"])
    return _make_svg_icon(svg, 16)


STYLE_GROUP = """
QGroupBox {
    color: #aaaaaa;
    border: 1px solid #3a3a4a;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
"""


# ---------------------------------------------------------------------------
# Thread de scan (non-bloquant)
# ---------------------------------------------------------------------------
class ScanThread(QThread):
    finished = pyqtSignal(list)  # [(device_id, name), ...]

    def __init__(self, hidden_ids: list[str] = None):
        super().__init__()
        self._hidden_ids = hidden_ids or []

    def run(self):
        results = scan_usb_list(self._hidden_ids)
        self.finished.emit(results)


# ---------------------------------------------------------------------------
# Widget d'une ligne d'action
# ---------------------------------------------------------------------------
class ActionRow(QWidget):
    removed = pyqtSignal(object)  # self

    # (label affiché, valeur interne)
    _TYPE_ITEMS = [
        ("▶  Lancer une app",     "run"),
        ("✕  Fermer une app",     "close"),
        ("⌨  Commande shell",     "command"),
        ("📂  Ouvrir un fichier", "file"),
    ]

    def __init__(self, action: Action = None, parent=None):
        super().__init__(parent)
        self.action = action or Action(type="run")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 2, 0, 4)
        root.setSpacing(3)

        # --- Ligne principale ---
        main_row = QHBoxLayout()
        main_row.setSpacing(6)

        self.type_box = QComboBox()
        for label, value in self._TYPE_ITEMS:
            self.type_box.addItem(label, value)
        _idx = next(
            (i for i in range(self.type_box.count())
             if self.type_box.itemData(i) == self.action.type), 0
        )
        self.type_box.setCurrentIndex(_idx)
        self.type_box.setFixedWidth(158)
        self.type_box.currentIndexChanged.connect(self._on_type_changed)
        self._update_type_tooltip(self.action.type)

        self.proc_edit = QLineEdit(self.action.process)
        self.proc_edit.setPlaceholderText("Processus (ex: opera.exe)")
        self.proc_edit.setToolTip("Nom exact du processus Windows (ex : opera.exe, Discord.exe)")

        self.path_edit = QLineEdit(self.action.path)
        self.path_edit.setPlaceholderText("Chemin ou commande")
        self.path_edit.setToolTip("Chemin complet vers l'exécutable ou la commande à lancer")

        # Bouton parcourir (stocké comme attribut pour contrôler la visibilité)
        self.browse_btn = QPushButton()
        self.browse_btn.setIcon(_icon_browse())
        self.browse_btn.setIconSize(QSize(15, 15))
        self.browse_btn.setFixedSize(30, 28)
        self.browse_btn.setToolTip("Parcourir pour choisir un fichier")
        self.browse_btn.setStyleSheet("""
            QPushButton { background: #2a2a4a; border: 1px solid #4040aa; border-radius: 5px; }
            QPushButton:hover  { background: #3a3a6a; border-color: #6060cc; }
            QPushButton:pressed { background: #5050aa; }
        """)
        self.browse_btn.clicked.connect(self._browse)

        # Bouton options avancées (icône engrenage)
        self.adv_btn = QPushButton()
        self.adv_btn.setIcon(_icon_settings())
        self.adv_btn.setIconSize(QSize(14, 14))
        self.adv_btn.setFixedSize(30, 28)
        self.adv_btn.setCheckable(True)
        self.adv_btn.setToolTip("Options avancées : masquage forcé, délai, condition")
        self.adv_btn.setStyleSheet("""
            QPushButton { background: #2a2a4a; border: 1px solid #4040aa; border-radius: 5px; }
            QPushButton:checked { background: #5050aa; border-color: #8080ff; }
            QPushButton:hover   { background: #3a3a6a; }
        """)
        self.adv_btn.toggled.connect(self._toggle_advanced)

        # Bouton supprimer
        remove_btn = QPushButton()
        remove_btn.setIcon(_icon_remove())
        remove_btn.setIconSize(QSize(15, 15))
        remove_btn.setFixedSize(30, 28)
        remove_btn.setToolTip("Supprimer cette action")
        remove_btn.setStyleSheet("""
            QPushButton { background: #3a1a1a; border: 1px solid #aa3333; border-radius: 5px; }
            QPushButton:hover  { background: #4a2020; border-color: #dd4444; }
            QPushButton:pressed { background: #6a2020; }
        """)
        remove_btn.clicked.connect(lambda: self.removed.emit(self))

        main_row.addWidget(self.type_box)
        main_row.addWidget(self.proc_edit)
        main_row.addWidget(self.path_edit)
        main_row.addWidget(self.browse_btn)
        main_row.addWidget(self.adv_btn)
        main_row.addWidget(remove_btn)
        root.addLayout(main_row)

        # ── Ligne args : chips + champ (une seule ligne, visible pour "run") ─
        self.args_widget = QWidget()
        args_row = QHBoxLayout(self.args_widget)
        args_row.setContentsMargins(0, 0, 0, 0)
        args_row.setSpacing(5)

        _PRESETS = [
            ("--minimized",       "Démarre dans le systray\n(Discord, lghub, Razer, Signal RGB…)"),
            ("--start-minimized", "Alternative à --minimized pour certaines apps"),
            ("--silent",          "Mode silencieux (sans popup de bienvenue)"),
        ]
        for arg, tip in _PRESETS:
            chip = QPushButton(arg)
            chip.setFixedHeight(22)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setToolTip(tip)
            chip.setStyleSheet("""
                QPushButton {
                    background: #162416; border: 1px solid #2a5a2a;
                    border-radius: 11px; color: #77bb77;
                    font-size: 8pt; padding: 0 9px;
                }
                QPushButton:hover { background: #1e3a1e; border-color: #44aa44; color: #aaeaaa; }
                QPushButton:pressed { background: #2a4a2a; }
            """)
            chip.clicked.connect(lambda checked, a=arg: self._add_preset_arg(a))
            args_row.addWidget(chip)

        self.args_edit = QLineEdit(self.action.args)
        self.args_edit.setPlaceholderText("Paramètres supplémentaires…")
        self.args_edit.setToolTip(
            "Arguments passés à l'exécutable au lancement.\n"
            "Cliquez sur un raccourci à gauche pour l'ajouter."
        )
        self.args_edit.setStyleSheet(
            "QLineEdit { background: #1e1e30; border: 1px solid #3a3a5a; "
            "border-radius: 4px; padding: 3px 6px; color: #c0c0e0; font-size: 9pt; }"
            "QLineEdit:focus { border-color: #6060cc; }"
        )
        args_row.addWidget(self.args_edit, stretch=1)
        root.addWidget(self.args_widget)

        # ── Panneau options avancées — 2 lignes, masqué par défaut ──────────
        self.adv_panel = QWidget()
        self.adv_panel.setObjectName("AdvPanel")
        self.adv_panel.setStyleSheet(
            "#AdvPanel { background: #22223a; border: 1px solid #3a3a5a; border-radius: 5px; }"
        )
        adv_outer = QVBoxLayout(self.adv_panel)
        adv_outer.setContentsMargins(10, 7, 10, 7)
        adv_outer.setSpacing(6)

        # Ligne 1 : masquage + délai
        adv_row1 = QHBoxLayout()
        adv_row1.setSpacing(12)

        self.start_hidden_check = QCheckBox("Masquage forcé  (si --minimized absent)")
        self.start_hidden_check.setChecked(self.action.start_hidden)
        self.start_hidden_check.setToolTip(
            "Cache la fenêtre via Windows, puis envoie WM_CLOSE dès que\n"
            "le CPU du processus est idle (initialisation terminée).\n"
            "À utiliser uniquement si l'app ne supporte pas --minimized.\n\n"
            "⚠ Si l'icône systray ne répond plus, désactivez cette option."
        )
        self.start_hidden_check.setStyleSheet("color: #aaaacc; font-size: 9pt;")
        adv_row1.addWidget(self.start_hidden_check)
        adv_row1.addStretch()

        delay_lbl = QLabel("Délai après (s) :")
        delay_lbl.setStyleSheet("color: #aaaacc; font-size: 9pt;")
        self.sleep_spin = QDoubleSpinBox()
        self.sleep_spin.setRange(0, 60)
        self.sleep_spin.setSingleStep(0.5)
        self.sleep_spin.setDecimals(1)
        self.sleep_spin.setValue(self.action.post_sleep or 0)
        self.sleep_spin.setFixedWidth(65)
        self.sleep_spin.setToolTip("Pause après l'action avant la suivante (secondes)")
        adv_row1.addWidget(delay_lbl)
        adv_row1.addWidget(self.sleep_spin)
        adv_outer.addLayout(adv_row1)

        # Ligne 2 : condition
        adv_row2 = QHBoxLayout()
        adv_row2.setSpacing(6)

        cond_lbl = QLabel("Condition :")
        cond_lbl.setStyleSheet("color: #aaaacc; font-size: 9pt;")
        cond_lbl.setFixedWidth(72)
        adv_row2.addWidget(cond_lbl)

        self.cond_edit = QLineEdit(self.action.condition)
        self.cond_edit.setPlaceholderText("device_present:Nom  &&  device_absent:Autre")
        self.cond_edit.setToolTip(
            "Conditions séparées par &&  (toutes doivent être vraies)\n"
            "  device_present:Nom  →  ce périphérique DOIT être connecté\n"
            "  device_absent:Nom   →  ce périphérique NE DOIT PAS être connecté"
        )
        adv_row2.addWidget(self.cond_edit, stretch=1)

        add_cond_present = QPushButton("＋ présent")
        add_cond_present.setFixedHeight(24)
        add_cond_present.setToolTip("Ajouter : si ce périphérique est connecté")
        add_cond_present.setStyleSheet(
            "QPushButton { font-size: 8pt; background: #1a2a1a; border: 1px solid #336633; border-radius: 4px; padding: 0 6px; }"
            "QPushButton:hover { background: #1a3a1a; border-color: #55aa55; }"
        )
        add_cond_present.clicked.connect(lambda: self._append_condition("device_present:"))
        adv_row2.addWidget(add_cond_present)

        add_cond_absent = QPushButton("＋ absent")
        add_cond_absent.setFixedHeight(24)
        add_cond_absent.setToolTip("Ajouter : si ce périphérique n'est PAS connecté")
        add_cond_absent.setStyleSheet(
            "QPushButton { font-size: 8pt; background: #2a1a1a; border: 1px solid #663333; border-radius: 4px; padding: 0 6px; }"
            "QPushButton:hover { background: #3a1a1a; border-color: #aa5555; }"
        )
        add_cond_absent.clicked.connect(lambda: self._append_condition("device_absent:"))
        adv_row2.addWidget(add_cond_absent)

        adv_outer.addLayout(adv_row2)
        self.adv_panel.setVisible(False)
        root.addWidget(self.adv_panel)

        self._on_type_changed()

        # Ouvrir le panneau si des options avancées sont déjà renseignées
        has_advanced = any([
            self.action.condition,
            self.action.post_sleep,
            self.action.start_hidden,
        ])
        if has_advanced:
            self.adv_btn.setChecked(True)

    def _update_type_tooltip(self, t: str):
        tips = {
            "run":     "▶  Lance un exécutable.\nIgnoré si le processus est déjà en cours.",
            "close":   "✕  Ferme un processus Windows par son nom de fichier.",
            "command": "⌨  Exécute une commande dans cmd / PowerShell.",
            "file":    "📂  Ouvre un fichier avec son application par défaut.",
        }
        self.type_box.setToolTip(tips.get(t, "Type d'action"))

    def _append_condition(self, prefix: str):
        current = self.cond_edit.text().strip()
        separator = " && " if current else ""
        self.cond_edit.setText(f"{current}{separator}{prefix}")
        self.cond_edit.setFocus()
        self.cond_edit.setCursorPosition(len(self.cond_edit.text()))

    def _toggle_advanced(self, checked: bool):
        self.adv_panel.setVisible(checked)

    def _on_type_changed(self, _=None):
        t = self.type_box.currentData() or "run"
        self._update_type_tooltip(t)
        is_close = t == "close"
        is_run   = t == "run"

        # Processus : visible pour run + close
        self.proc_edit.setVisible(t in ("run", "close"))
        self.proc_edit.setPlaceholderText(
            "Processus à fermer  (ex : discord.exe)" if is_close
            else "Processus  (ex : Discord.exe)"
        )

        # Chemin + parcourir : inutiles pour close (on ferme par nom de process)
        self.path_edit.setVisible(not is_close)
        self.browse_btn.setVisible(not is_close)
        self.path_edit.setPlaceholderText(
            "Chemin vers l'exécutable  (.exe ou raccourci .lnk)" if is_run
            else "Commande  (ex : taskkill /f /im app.exe)"      if t == "command"
            else "Chemin vers le fichier à ouvrir"
        )

        # Paramètres + avancé : uniquement pour "run"
        self.args_widget.setVisible(is_run)
        self.adv_btn.setVisible(is_run)
        if not is_run:
            self.adv_panel.setVisible(False)

    def _add_preset_arg(self, arg: str):
        """Ajoute un argument préset dans le champ args (sans doublon)."""
        current = self.args_edit.text().strip()
        if arg not in current:
            self.args_edit.setText((current + " " + arg).strip())

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un exécutable",
            filter="Exécutables (*.exe);;Tous les fichiers (*.*)"
        )
        if path:
            path = path.replace("/", "\\")
            self.path_edit.setText(path)
            exe_name = path.split("\\")[-1]
            if not self.proc_edit.text():
                self.proc_edit.setText(exe_name)

    def get_action(self) -> Action:
        t = self.type_box.currentData() or "run"
        return Action(
            type=t,
            process=self.proc_edit.text().strip(),
            path=self.path_edit.text().strip() if t != "close" else "",
            args=self.args_edit.text().strip()          if t == "run" else "",
            condition=self.cond_edit.text().strip()     if t == "run" else "",
            post_sleep=self.sleep_spin.value()          if t == "run" else 0,
            wait_window="",         # retiré de l'UI (trop edge-case)
            wait_window_action="",  # retiré de l'UI
            start_hidden=self.start_hidden_check.isChecked() if t == "run" else False,
        )


# ---------------------------------------------------------------------------
# Widget liste d'actions
# ---------------------------------------------------------------------------
class ActionList(QWidget):
    def __init__(self, title: str, color: str, actions: list[Action] = None,
                 tooltip: str = "", on_change=None, parent=None):
        super().__init__(parent)
        self.rows: list[ActionRow] = []
        self._on_change = on_change  # callback appelé après ajout/suppression/toggle

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox(title)
        group.setStyleSheet(
            f"QGroupBox {{ color: {color}; border: 1px solid #3a3a4a; "
            f"border-radius:6px; margin-top:10px; padding-top:10px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left:10px; padding: 0 6px; font-size: 9pt; }}"
        )
        if tooltip:
            group.setToolTip(tooltip)

        self.inner_layout = QVBoxLayout(group)
        self.inner_layout.setSpacing(4)
        self.inner_layout.setContentsMargins(8, 4, 8, 8)

        add_btn = QPushButton("＋  Ajouter une action")
        add_btn.setToolTip("Ajouter une nouvelle action à cette liste")
        add_btn.setStyleSheet(
            f"QPushButton {{ color: {color}; background: transparent; "
            f"border: 1px dashed {color}; border-radius: 4px; padding: 5px; font-size: 9pt; }}"
            f"QPushButton:hover {{ background: rgba(255,255,255,0.05); }}"
        )
        add_btn.clicked.connect(self.add_row)

        self.inner_layout.addWidget(add_btn)
        outer.addWidget(group)

        for a in (actions or []):
            self._insert_row(ActionRow(a))

    def _insert_row(self, row: ActionRow):
        self.rows.append(row)
        # Insérer avant le bouton "Ajouter" (dernier item)
        self.inner_layout.insertWidget(self.inner_layout.count() - 1, row)
        row.removed.connect(self._remove_row)
        # Redimensionner quand le panneau avancé s'ouvre/ferme
        row.adv_btn.toggled.connect(self._notify_change)
        self._notify_change()

    def add_row(self):
        self._insert_row(ActionRow())

    def _remove_row(self, row: ActionRow):
        self.rows.remove(row)
        self.inner_layout.removeWidget(row)
        row.deleteLater()
        self._notify_change()

    def _notify_change(self, *_):
        if self._on_change:
            QTimer.singleShot(0, self._on_change)

    def get_actions(self) -> list[Action]:
        return [r.get_action() for r in self.rows]


# ---------------------------------------------------------------------------
# Wizard principal
# ---------------------------------------------------------------------------
class DeviceWizard(QDialog):
    def __init__(self, config: Config, device: Device = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.editing = device
        self.usb_list: list[tuple[str, str]] = []
        self.result_device: Device | None = None

        self.setWindowTitle("Ajouter un périphérique" if not device else "Modifier le périphérique")
        self.setMinimumSize(700, 520)
        self.resize(780, 600)
        self.setStyleSheet("""
            QDialog { background: #1e1e2e; color: #f0f0f0; }
            QLabel  { color: #f0f0f0; }
            QLineEdit, QComboBox {
                background: #2a2a3e; color: #f0f0f0;
                border: 1px solid #3a3a4a; border-radius: 4px; padding: 4px 6px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #6060cc; }
            QPushButton {
                background: #2a2a3e; color: #f0f0f0;
                border: 1px solid #3a3a4a; border-radius: 4px;
                padding: 5px 12px;
            }
            QPushButton:hover   { background: #3a3a5a; }
            QPushButton:pressed { background: #5050aa; }
            QCheckBox { color: #f0f0f0; }
        """)

        self._build_ui()

        if device:
            self._fill_from_device(device)

        # Adapter la taille initiale au contenu
        QTimer.singleShot(0, self._fit_to_content)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # --- Bandeau d'étape ---
        step_bar = QHBoxLayout()
        step_bar.setSpacing(8)

        self.step_label = QLabel("Étape 1 / 2")
        self.step_label.setStyleSheet(
            "color: #ffffff; background: #5050aa; border-radius: 4px; "
            "padding: 2px 10px; font-size: 10px; font-weight: bold;"
        )
        self.step_label.setFixedHeight(22)

        self.step_desc = QLabel("Identification du périphérique")
        self.step_desc.setStyleSheet("color: #aaaacc; font-size: 10px;")

        step_bar.addWidget(self.step_label)
        step_bar.addWidget(self.step_desc)
        step_bar.addStretch()
        main_layout.addLayout(step_bar)

        # Séparateur
        from PyQt6.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #2a2a4a; background: #2a2a4a; max-height: 1px;")
        main_layout.addWidget(sep)

        # Pages
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self._build_page1()
        self._build_page2()

        # --- Boutons navigation ---
        from PyQt6.QtWidgets import QFrame as QFrame2
        sep2 = QFrame2()
        sep2.setFrameShape(QFrame2.Shape.HLine)
        sep2.setStyleSheet("color: #2a2a4a; background: #2a2a4a; max-height: 1px;")
        main_layout.addWidget(sep2)

        btn_row = QHBoxLayout()
        self.prev_btn = QPushButton("← Précédent")
        self.prev_btn.setToolTip("Retourner à l'étape d'identification")
        self.prev_btn.clicked.connect(self._prev)
        self.prev_btn.setVisible(False)

        self.next_btn = QPushButton("Suivant →")
        self.next_btn.setToolTip("Passer à la configuration des actions")
        self.next_btn.clicked.connect(self._next)
        self.next_btn.setStyleSheet(
            "QPushButton { background: #5050aa; border-color: #6060cc; } "
            "QPushButton:hover { background: #6060cc; }"
        )

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setToolTip("Fermer sans enregistrer")
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(self.prev_btn)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.next_btn)
        main_layout.addLayout(btn_row)

    # ---- Page 1 : Identification ----
    def _build_page1(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(8)

        # Texte d'intro
        intro = QLabel(
            "Cliquez pour sélectionner un périphérique · "
            "Ctrl+clic pour en sélectionner plusieurs · "
            "Entrée pour valider"
        )
        intro.setStyleSheet("color: #8888aa; font-size: 9pt; font-style: italic;")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # Barre filtre + bouton scan
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("🔍  Filtrer les périphériques…")
        self.filter_edit.setToolTip("Filtrer la liste par nom ou identifiant")
        self.filter_edit.textChanged.connect(self._apply_device_filter)
        self.filter_edit.setStyleSheet(
            "QLineEdit { background: #22223a; border: 1px solid #3a3a5a; "
            "border-radius: 4px; padding: 4px 8px; color: #d0d0e0; }"
            "QLineEdit:focus { border-color: #6060cc; }"
        )

        self.scan_btn = QPushButton("⟳  Scanner")
        self.scan_btn.setFixedWidth(95)
        self.scan_btn.setToolTip("Actualiser la liste des périphériques détectés")
        self.scan_btn.clicked.connect(self._start_scan)

        top_row.addWidget(self.filter_edit, stretch=1)
        top_row.addWidget(self.scan_btn)
        layout.addLayout(top_row)

        # Liste multi-sélection
        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.device_list.setFixedHeight(190)
        self.device_list.setIconSize(QSize(16, 16))
        self.device_list.setStyleSheet("""
            QListWidget {
                background: #1a1a2a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 2px;
                outline: none;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 3px;
                color: #d0d0e0;
            }
            QListWidget::item:selected {
                background: #4040aa;
                color: #ffffff;
            }
            QListWidget::item:hover:!selected {
                background: #2a2a4a;
            }
        """)
        self.device_list.currentItemChanged.connect(self._on_device_selected)
        layout.addWidget(self.device_list)

        # Boutons de gestion
        manage_row = QHBoxLayout()
        manage_row.setSpacing(6)

        hide_btn = QPushButton("🚫  Masquer la sélection")
        hide_btn.setFixedHeight(24)
        hide_btn.setToolTip("Masquer le ou les périphériques sélectionnés des futurs scans")
        hide_btn.setStyleSheet(
            "QPushButton { font-size: 9pt; background: #2a1a2a; border: 1px solid #663366; border-radius: 4px; padding: 1px 8px; }"
            "QPushButton:hover { background: #3a1a3a; border-color: #aa44aa; }"
        )
        hide_btn.clicked.connect(self._hide_selected)

        hide_int_btn = QPushButton("🤖  Masquer les internes")
        hide_int_btn.setFixedHeight(24)
        hide_int_btn.setToolTip("Masquer automatiquement les périphériques système/hubs/volumes internes")
        hide_int_btn.setStyleSheet(
            "QPushButton { font-size: 9pt; background: #1a1a2a; border: 1px solid #334466; border-radius: 4px; padding: 1px 8px; }"
            "QPushButton:hover { background: #1a1a3a; border-color: #5566aa; }"
        )
        hide_int_btn.clicked.connect(self._hide_internals)

        reset_btn = QPushButton("↺  Réinitialiser")
        reset_btn.setFixedHeight(24)
        reset_btn.setToolTip("Afficher à nouveau tous les périphériques masqués")
        reset_btn.setStyleSheet(
            "QPushButton { font-size: 9pt; background: #1a2a1a; border: 1px solid #336633; border-radius: 4px; padding: 1px 8px; }"
            "QPushButton:hover { background: #1a3a1a; border-color: #55aa55; }"
        )
        reset_btn.clicked.connect(self._reset_hidden)

        manage_row.addWidget(hide_btn)
        manage_row.addWidget(hide_int_btn)
        manage_row.addStretch()
        manage_row.addWidget(reset_btn)
        layout.addLayout(manage_row)

        self.scan_status = QLabel("⟳  Scan en cours…")
        self.scan_status.setStyleSheet("color: #6666aa; font-size: 9px;")
        layout.addWidget(self.scan_status)

        # Séparateur "ou saisir manuellement"
        sep_row = QHBoxLayout()
        sep_line_l = QLabel()
        sep_line_l.setStyleSheet("background: #3a3a4a; max-height: 1px;")
        sep_line_l.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sep_or = QLabel("  ou saisir manuellement  ")
        sep_or.setStyleSheet("color: #555577; font-size: 9px;")
        sep_line_r = QLabel()
        sep_line_r.setStyleSheet("background: #3a3a4a; max-height: 1px;")
        sep_line_r.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sep_row.addWidget(sep_line_l)
        sep_row.addWidget(sep_or)
        sep_row.addWidget(sep_line_r)
        layout.addLayout(sep_row)

        # Champs manuels
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("ex: VID_046D&PID_0AB7&MI  ou  Razer Tartarus")
        self.id_edit.setToolTip("Fragment unique de l'identifiant Windows du périphérique")
        form.addRow("Identifiant :", self.id_edit)

        self.match_combo = QComboBox()
        self.match_combo.addItems(["contains", "exact", "regex"])
        self.match_combo.setToolTip("Mode de correspondance pour reconnaître le périphérique")
        self.match_combo.currentTextChanged.connect(self._update_match_hint)
        form.addRow("Correspondance :", self.match_combo)

        self.match_hint = QLabel()
        self.match_hint.setStyleSheet("color: #44aa88; font-size: 9px; font-style: italic;")
        form.addRow("", self.match_hint)

        layout.addLayout(form)

        # Section conditions d'exécution
        cond_group = QGroupBox("Conditions d'exécution")
        cond_group.setStyleSheet(STYLE_GROUP)
        cond_group.setToolTip(
            "Définissez des conditions qui doivent être remplies pour que les actions\n"
            "de ce périphérique s'exécutent (connexion et déconnexion)."
        )
        cond_layout = QVBoxLayout(cond_group)
        cond_layout.setSpacing(6)
        cond_layout.setContentsMargins(10, 10, 10, 10)

        cond_info = QLabel(
            "Les actions ne s'exécuteront que si toutes les conditions sont vraies.\n"
            "Exemple : bloquer les actions si un autre périphérique spécifique est présent."
        )
        cond_info.setStyleSheet("color: #8888aa; font-size: 9px; font-style: italic;")
        cond_info.setWordWrap(True)
        cond_layout.addWidget(cond_info)

        cond_row = QHBoxLayout()
        cond_row.setSpacing(6)

        self.exec_cond_edit = QLineEdit()
        self.exec_cond_edit.setPlaceholderText("device_present:Nom  &&  device_absent:Autre")
        self.exec_cond_edit.setToolTip(
            "Conditions séparées par &&  (toutes doivent être vraies)\n"
            "  device_present:Nom  ->  ce périphérique DOIT être connecté\n"
            "  device_absent:Nom   ->  ce périphérique NE DOIT PAS être connecté"
        )
        cond_row.addWidget(self.exec_cond_edit, stretch=1)

        add_present_btn = QPushButton("+ présent")
        add_present_btn.setFixedHeight(24)
        add_present_btn.setToolTip("Ajouter : si ce périphérique est connecté")
        add_present_btn.setStyleSheet(
            "QPushButton { font-size: 8pt; background: #1a2a1a; border: 1px solid #336633; border-radius: 4px; padding: 0 6px; }"
            "QPushButton:hover { background: #1a3a1a; border-color: #55aa55; }"
        )
        add_present_btn.clicked.connect(lambda: self._append_exec_condition("device_present:"))
        cond_row.addWidget(add_present_btn)

        add_absent_btn = QPushButton("+ absent")
        add_absent_btn.setFixedHeight(24)
        add_absent_btn.setToolTip("Ajouter : si ce périphérique n'est PAS connecté")
        add_absent_btn.setStyleSheet(
            "QPushButton { font-size: 8pt; background: #2a1a1a; border: 1px solid #663333; border-radius: 4px; padding: 0 6px; }"
            "QPushButton:hover { background: #3a1a1a; border-color: #aa5555; }"
        )
        add_absent_btn.clicked.connect(lambda: self._append_exec_condition("device_absent:"))
        cond_row.addWidget(add_absent_btn)

        cond_layout.addLayout(cond_row)
        layout.addWidget(cond_group)

        layout.addStretch()

        self.stack.addWidget(page)
        self._update_match_hint("contains")
        # Lancer un scan auto au démarrage
        self._start_scan()

    def _update_match_hint(self, mode: str):
        hints = {
            "contains": "✔ Vrai si l'identifiant contient ce texte (recommandé)",
            "exact":    "✔ Vrai si l'identifiant correspond exactement à une ligne",
            "regex":    "✔ Vrai si l'identifiant correspond à l'expression régulière",
        }
        self.match_hint.setText(hints.get(mode, ""))

    def _append_exec_condition(self, prefix: str):
        current = self.exec_cond_edit.text().strip()
        separator = " && " if current else ""
        self.exec_cond_edit.setText(f"{current}{separator}{prefix}")
        self.exec_cond_edit.setFocus()
        self.exec_cond_edit.setCursorPosition(len(self.exec_cond_edit.text()))

    def _start_scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_status.setText("⟳  Scan en cours…")
        self.scan_status.setStyleSheet("color: #6666aa; font-size: 9px;")
        self._scan_thread = ScanThread(self.config.hidden_scan_ids)
        self._scan_thread.finished.connect(self._on_scan_done)
        self._scan_thread.start()

    def _on_scan_done(self, results: list[tuple[str, str]]):
        self.usb_list = results
        self.scan_btn.setEnabled(True)
        self.device_list.clear()
        for dev_id, name in results:
            label = f"{name}  —  {dev_id}" if name else dev_id
            icon = _device_icon(get_device_type(dev_id, name))
            item = QListWidgetItem(icon, label)
            item.setData(Qt.ItemDataRole.UserRole, dev_id)
            self.device_list.addItem(item)
        n = len(results)
        n_hidden = len(self.config.hidden_scan_ids)
        hidden_txt = f"  ·  {n_hidden} masqué{'s' if n_hidden > 1 else ''}" if n_hidden else ""
        self.scan_status.setText(
            f"✔  {n} périphérique{'s' if n > 1 else ''} détecté{'s' if n > 1 else ''} (USB, HID, HDMI){hidden_txt}."
        )
        self.scan_status.setStyleSheet("color: #44aa88; font-size: 9px;")
        self._apply_device_filter(self.filter_edit.text())

    def _apply_device_filter(self, text: str):
        keyword = text.strip().lower()
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            item.setHidden(bool(keyword) and keyword not in item.text().lower())

    def _on_device_selected(self, current: QListWidgetItem, _previous):
        if current:
            dev_id = current.data(Qt.ItemDataRole.UserRole)
            if dev_id:
                self.id_edit.setText(dev_id)

    def _hide_selected(self):
        selected = self.device_list.selectedItems()
        added = False
        for item in selected:
            dev_id = item.data(Qt.ItemDataRole.UserRole)
            if dev_id and dev_id not in self.config.hidden_scan_ids:
                self.config.hidden_scan_ids.append(dev_id)
                added = True
        if added:
            self.config.save()
            self._start_scan()

    def _hide_internals(self):
        added = False
        for dev_id, name in self.usb_list:
            if is_internal_device(dev_id, name) and dev_id not in self.config.hidden_scan_ids:
                self.config.hidden_scan_ids.append(dev_id)
                added = True
        if added:
            self.config.save()
            self._start_scan()

    def _reset_hidden(self):
        self.config.hidden_scan_ids.clear()
        self.config.save()
        self._start_scan()

    # ---- Page 2 : Nom, options, actions ----
    def _build_page2(self):
        from PyQt6.QtWidgets import QScrollArea as _SA
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 4, 0, 0)

        # ── Nom + option de confirmation ─────────────────────────────────────
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(8)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("ex : Clavier Corsair, Manette, Micro Logitech…")
        self.name_edit.setToolTip("Nom affiché dans la liste principale de l'application")
        form.addRow("Nom :", self.name_edit)

        self.confirm_check = QCheckBox("Demander confirmation avant de fermer les applications")
        self.confirm_check.setToolTip(
            "Si coché, une boîte de dialogue s'affichera lors de la déconnexion\n"
            "avant d'exécuter les actions de fermeture."
        )
        form.addRow("Options :", self.confirm_check)
        layout.addLayout(form)

        # ── Listes d'actions dans un scroll area ─────────────────────────────
        actions_container = QWidget()
        actions_container.setStyleSheet("background: transparent;")
        acts_layout = QVBoxLayout(actions_container)
        acts_layout.setContentsMargins(0, 0, 4, 0)
        acts_layout.setSpacing(10)

        self.con_list = ActionList(
            "⚡  Actions à la CONNEXION", "#00cc66",
            tooltip="Actions exécutées automatiquement quand ce périphérique est branché",
        )
        self.dis_list = ActionList(
            "✖  Actions à la DÉCONNEXION", "#dd4444",
            tooltip="Actions exécutées automatiquement quand ce périphérique est retiré",
        )
        acts_layout.addWidget(self.con_list)
        acts_layout.addWidget(self.dis_list)

        scroll = _SA()
        scroll.setWidget(actions_container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setMinimumHeight(200)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical { background: #1a1a2a; width: 6px; border-radius: 3px; }"
            "QScrollBar::handle:vertical { background: #3a3a6a; border-radius: 3px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        layout.addWidget(scroll, stretch=1)

        self.stack.addWidget(page)

    def _fill_from_device(self, d: Device):
        self.id_edit.setText(d.id)
        self.match_combo.setCurrentText(d.match_type)
        self._update_match_hint(d.match_type)
        self.exec_cond_edit.setText(d.execution_condition)
        self.name_edit.setText(d.name)
        self.confirm_check.setChecked(d.confirm_on_disconnect)
        # Remplir les actions — on passe directement à la page 2
        self._go_to_page2()
        for a in d.on_connect:
            self.con_list._insert_row(ActionRow(a))
        for a in d.on_disconnect:
            self.dis_list._insert_row(ActionRow(a))

    # ---- Navigation ----
    def _fit_to_content(self):
        """Adapte la taille au contenu selon la page affichée."""
        if self.stack.currentIndex() == 0:
            # Page 1 : contenu fixe, pas de scroll → ajustement exact
            self.adjustSize()
            # S'assurer qu'on reste au-dessus du minimum
            if self.width() < 700:
                self.resize(700, self.height())
        else:
            # Page 2 : le scroll area gère la hauteur → garantir largeur minimale
            if self.width() < 700:
                self.resize(700, self.height())

    def _go_to_page2(self):
        self.stack.setCurrentIndex(1)
        self.prev_btn.setVisible(True)
        self.next_btn.setText("💾  Enregistrer")
        self.next_btn.setToolTip("Enregistrer la configuration de ce périphérique")
        self.step_label.setText("Étape 2 / 2")
        self.step_desc.setText("Configuration des actions")
        QTimer.singleShot(0, self._fit_to_content)

    def _prev(self):
        self.stack.setCurrentIndex(0)
        self.prev_btn.setVisible(False)
        self.next_btn.setText("Suivant →")
        self.next_btn.setToolTip("Passer à la configuration des actions")
        self.step_label.setText("Étape 1 / 2")
        self.step_desc.setText("Identification du périphérique")
        QTimer.singleShot(0, self._fit_to_content)

    def _next(self):
        if self.stack.currentIndex() == 0:
            if not self.id_edit.text().strip():
                QMessageBox.warning(self, "USB Detect", "Veuillez renseigner un identifiant de périphérique.")
                return
            self._go_to_page2()
        else:
            self._save()

    def _save(self):
        name = self.name_edit.text().strip() or "Nouveau périphérique"
        dev_id = self.id_edit.text().strip()
        match_type = self.match_combo.currentText()
        exec_condition = self.exec_cond_edit.text().strip()
        confirm = self.confirm_check.isChecked()
        on_connect = self.con_list.get_actions()
        on_disconnect = self.dis_list.get_actions()

        if self.editing:
            self.editing.name = name
            self.editing.id = dev_id
            self.editing.match_type = match_type
            self.editing.execution_condition = exec_condition
            self.editing.confirm_on_disconnect = confirm
            self.editing.on_connect = on_connect
            self.editing.on_disconnect = on_disconnect
            self.result_device = self.editing
        else:
            self.result_device = Device(
                name=name, id=dev_id, match_type=match_type,
                execution_condition=exec_condition,
                confirm_on_disconnect=confirm,
                on_connect=on_connect, on_disconnect=on_disconnect,
            )
        self.accept()
