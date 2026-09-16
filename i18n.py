"""
USB Detect - Internationalisation (i18n)

Système de traduction léger.

Le texte source (en français) sert directement de clé de traduction :
  - en mode "fr", tr() retourne le texte tel quel ;
  - en mode "en", tr() retourne la traduction anglaise, ou le texte source
    si aucune traduction n'existe (fallback).

Pour les chaînes avec valeurs dynamiques, utiliser un gabarit avec
placeholders nommés puis .format() :
    tr("Version actuelle : v{v}").format(v=APP_VERSION)
"""

import locale

_LANG = "fr"

LANGUAGES = {
    "fr": "Français",
    "en": "English",
}


def set_language(lang: str):
    """Définit la langue courante ('fr' ou 'en')."""
    global _LANG
    _LANG = lang if lang in LANGUAGES else "fr"


def get_language() -> str:
    return _LANG


def tr(text: str) -> str:
    """Traduit un texte (le texte français source sert de clé)."""
    if _LANG == "fr":
        return text
    return _EN.get(text, text)


def detect_system_language() -> str:
    """Détecte la langue du système : 'fr' si locale française, sinon 'en'."""
    try:
        lang = locale.getdefaultlocale()[0] or ""
    except Exception:
        lang = ""
    return "fr" if lang.lower().startswith("fr") else "en"


def init_language():
    """Initialise la langue au démarrage.

    Priorité : valeur enregistrée dans config.json > locale système > 'fr'.
    Appelé tôt dans main(), avant la construction de l'UI.
    """
    lang = None
    try:
        import json
        from engine import CONFIG_PATH  # import tardif → évite les cycles
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            lang = (data.get("general", {}).get("language") or "").strip() or None
    except Exception:
        lang = None
    if not lang:
        lang = detect_system_language()
    set_language(lang)


# ---------------------------------------------------------------------------
# Traductions FR -> EN
# ---------------------------------------------------------------------------
_EN = {
    # ---- Général / commun ----
    "Erreur": "Error",
    "Annuler": "Cancel",
    "Sauvegarder": "Save",
    "Ajouter": "Add",
    "Effacer": "Clear",
    "Importer": "Import",
    "Exporter": "Export",
    "Import": "Import",
    "Export": "Export",
    "Vérifier": "Check",
    "USB Detect": "USB Detect",

    # ---- Visionneuse de logs ----
    "📋  Logs — USB Detect": "📋  Logs — USB Detect",
    "🔍  Filtrer les lignes…": "🔍  Filter lines…",
    "Affiche uniquement les lignes contenant ce texte":
        "Show only lines containing this text",
    "⬆  Aller en haut": "⬆  Go to top",
    "Défiler jusqu'à la dernière entrée de log":
        "Scroll to the latest log entry",
    "🗑  Effacer la vue": "🗑  Clear view",
    "Vider l'affichage (ne supprime pas le fichier de log)":
        "Clear the display (does not delete the log file)",
    "⟳  Actualisation auto · 0 lignes": "⟳  Auto-refresh · 0 lines",
    "⟳  Actualisation auto · {n} {lines}": "⟳  Auto-refresh · {n} {lines}",
    "ligne": "line",
    "lignes": "lines",
    "Aucun log disponible.": "No logs available.",
    "Vue effacée · Cliquez sur ⟳ Scanner pour recharger":
        "View cleared · Click ⟳ Scan to reload",
    "Vue effacée — appuyez sur Entrée pour recharger":
        "View cleared — press Enter to reload",

    # ---- Paramètres ----
    "Paramètres — USB Detect": "Settings — USB Detect",
    "Paramètres": "Settings",
    "Démarrage": "Startup",
    "Lancer USB Detect au démarrage de Windows":
        "Launch USB Detect at Windows startup",
    "Démarrer en arrière-plan (system tray)":
        "Start in the background (system tray)",
    "Démarrer fenêtre minimisée": "Start window minimized",
    "Notifications": "Notifications",
    "Activer les notifications": "Enable notifications",
    "Activer les logs": "Enable logs",
    "Configuration": "Configuration",
    "Sauvegardez vos macros avant une mise à jour":
        "Back up your macros before an update",
    "Mises à jour": "Updates",
    "Version actuelle : v{v}": "Current version: v{v}",
    "Installer la mise à jour": "Install update",
    "Langue": "Language",
    "Choisissez la langue de l'interface":
        "Choose the interface language",
    "La langue sera appliquée après redémarrage.":
        "The language will be applied after restart.",
    "Exporter la configuration": "Export configuration",
    "Configuration exportée vers :\n{path}":
        "Configuration exported to:\n{path}",
    "Impossible d'exporter :\n{e}": "Could not export:\n{e}",
    "Importer une configuration": "Import a configuration",
    "Ce fichier n'est pas une configuration USB Detect valide.":
        "This file is not a valid USB Detect configuration.",
    "Configuration importée avec succès.\nRedémarrez USB Detect pour appliquer les changements.":
        "Configuration imported successfully.\nRestart USB Detect to apply the changes.",
    "Impossible d'importer :\n{e}": "Could not import:\n{e}",
    "Vérification…": "Checking…",
    "v{version} disponible !": "v{version} available!",
    "Vous êtes à jour.": "You are up to date.",
    "Aucun fichier de mise à jour trouvé dans la release.":
        "No update file found in the release.",
    "Connexion…": "Connecting…",
    "Prêt ! Redémarrage…": "Ready! Restarting…",
    "Mise à jour prête": "Update ready",
    "La mise à jour a été téléchargée.\n\nUSB Detect va se fermer et l'installateur va démarrer.\nAcceptez la demande d'autorisation Windows pour finaliser.\nVotre configuration sera conservée.\n\nContinuer ?":
        "The update has been downloaded.\n\nUSB Detect will close and the installer will start.\n"
        "Accept the Windows permission prompt to finish.\nYour configuration will be preserved.\n\nContinue?",
    "Mise à jour en attente": "Update pending",
    "Erreur de mise à jour": "Update error",
    "Le téléchargement a échoué :\n{info}": "The download failed:\n{info}",

    # ---- Carte périphérique ----
    "Statut de connexion du périphérique": "Device connection status",
    "Moniteur HDMI/DisplayPort": "HDMI/DisplayPort monitor",
    "Clavier": "Keyboard",
    "Souris": "Mouse",
    "Hub USB": "USB hub",
    "Audio": "Audio",
    "Manette": "Gamepad",
    "Périphérique HID": "HID device",
    "Périphérique USB": "USB device",
    "Périphérique": "Device",
    "connexion": "connect",
    "connexions": "connects",
    "déconnexion": "disconnect",
    "déconnexions": "disconnects",
    "contient": "contains",
    "exact": "exact",
    "regex": "regex",
    "ID : {id}": "ID: {id}",
    "Identifiant complet :\n{id}": "Full identifier:\n{id}",
    "Simuler une CONNEXION\n{n} {actions} à exécuter\n(sans brancher le périphérique · conditions ignorées)":
        "Simulate a CONNECTION\n{n} {actions} to run\n(no need to plug the device in · conditions ignored)",
    "Simuler une DÉCONNEXION\n{n} {actions} à exécuter\n(sans débrancher le périphérique · conditions ignorées)":
        "Simulate a DISCONNECTION\n{n} {actions} to run\n(no need to unplug the device · conditions ignored)",
    "action": "action",
    "actions": "actions",
    "Activer / Désactiver ce macro": "Enable / disable this macro",
    "Modifier la configuration de ce périphérique":
        "Edit this device's configuration",
    "Supprimer définitivement ce périphérique et ses actions":
        "Permanently delete this device and its actions",
    "Activé": "Enabled",
    "Désactivé": "Disabled",
    "Type : {type}\nNom : {name}\nIdentifiant : {id}\nCorrespondance : {match}\nStatut : {status}":
        "Type: {type}\nName: {name}\nIdentifier: {id}\nMatching: {match}\nStatus: {status}",
    "DÉSACTIVÉ": "DISABLED",
    "CONNECTÉ": "CONNECTED",
    "DÉCONNECTÉ": "DISCONNECTED",

    # ---- Fenêtre principale ----
    "Initialisation…": "Initializing…",
    "Nouvelle version disponible : v{version}":
        "New version available: v{version}",
    "Mettre à jour": "Update",
    "USB Detect  v{v}": "USB Detect  v{v}",
    "Aucun périphérique configuré": "No device configured",
    "{n} périphérique  ·  aucun connecté": "{n} device  ·  none connected",
    "{n} périphériques  ·  aucun connecté": "{n} devices  ·  none connected",
    "{n} périphérique  ·  {c} connecté": "{n} device  ·  {c} connected",
    "{n} périphériques  ·  {c} connecté": "{n} devices  ·  {c} connected",
    "{n} périphériques  ·  {c} connectés": "{n} devices  ·  {c} connected",
    "＋  Ajouter un périphérique": "＋  Add a device",
    "Configurer un nouveau périphérique USB et ses actions automatiques":
        "Configure a new USB device and its automatic actions",
    "⟳  Initialisation…": "⟳  Initializing…",
    "⟳  Dernier scan : {time}": "⟳  Last scan: {time}",
    "Scan automatique toutes les 5 secondes via WMI":
        "Automatic scan every 5 seconds via WMI",
    "Ouvrir les paramètres de l'application":
        "Open the application settings",
    "Logs": "Logs",
    "Ouvrir la visionneuse de logs intégrée":
        "Open the built-in log viewer",
    "Cliquez sur  ＋ Ajouter un périphérique  pour commencer.\nChaque périphérique peut déclencher des actions\nautomatiques à la connexion ou déconnexion USB.":
        "Click  ＋ Add a device  to get started.\nEach device can trigger automatic actions\nwhen connected or disconnected via USB.",

    # ---- Systray ----
    "Afficher": "Show",
    "Ajouter un périphérique": "Add a device",
    "Recharger la config": "Reload config",
    "Ouvrir les logs": "Open logs",
    "Quitter": "Quit",
    "USB Detect — {n} périphérique(s), aucun connecté":
        "USB Detect — {n} device(s), none connected",
    "USB Detect — {c}/{n} connecté(s)\n{names}{suffix}":
        "USB Detect — {c}/{n} connected\n{names}{suffix}",

    # ---- Dialogues / notifications ----
    "{name} a été déconnecté.\n\nFermer les applications associées ?":
        "{name} has been disconnected.\n\nClose the associated applications?",
    "Périphérique ajouté": "Device added",
    "{name} configuré.": "{name} configured.",
    "Périphérique modifié": "Device edited",
    "Supprimer": "Delete",
    "Supprimer « {name} » et toutes ses actions ?":
        "Delete “{name}” and all its actions?",
    "{name} activé": "{name} enabled",
    "{name} désactivé": "{name} disabled",
    "Test": "Test",
    "Simulation connexion : {name}": "Connection simulation: {name}",
    "Simulation déconnexion : {name}": "Disconnection simulation: {name}",
    "Configuration rechargée.": "Configuration reloaded.",
    "Paramètres sauvegardés.": "Settings saved.",
    "Toujours actif dans la barre des tâches.":
        "Still running in the system tray.",
    "Une instance est déjà en cours d'exécution.":
        "An instance is already running.",

    # ---- Premier lancement / Quoi de neuf ----
    "Bienvenue — USB Detect": "Welcome — USB Detect",
    "<h3>Bienvenue dans USB Detect !</h3><p>Ce logiciel a été <b>entièrement concu avec l'aide d'une intelligence artificielle</b>.</p><p>Il est le fruit d'un besoin personnel : je n'ai trouvé aucune alternative satisfaisante en ligne pour automatiser des actions en fonction de mes peripheriques USB. Pendant longtemps, j'ai utilisé un petit script AutoHotkey bancal et potentiellement dangereux pour mon système.</p><p>USB Detect remplace cette solution artisanale par une interface propre, fiable et configurable.</p><hr><p><i>Projet open-source — contributions bienvenues sur GitHub.</i></p>":
        "<h3>Welcome to USB Detect!</h3><p>This software was <b>designed entirely with the help of artificial intelligence</b>.</p><p>It grew out of a personal need: I couldn't find any satisfactory online alternative to automate actions based on my USB devices. For a long time, I relied on a small, shaky AutoHotkey script that was potentially dangerous for my system.</p><p>USB Detect replaces that homemade solution with a clean, reliable and configurable interface.</p><hr><p><i>Open-source project — contributions welcome on GitHub.</i></p>",
    "Quoi de neuf — USB Detect v{v}": "What's new — USB Detect v{v}",
    "<h3>Nouveautés</h3>{entries}<hr><p><i>Merci d'utiliser USB Detect !</i></p>":
        "<h3>What's new</h3>{entries}<hr><p><i>Thank you for using USB Detect!</i></p>",

    # ---- Installation / mise à jour / désinstallation ----
    "USB Detect — Désinstallation": "USB Detect — Uninstall",
    "Voulez-vous désinstaller USB Detect ?\n\nVotre configuration (macros) sera sauvegardée sur le bureau.":
        "Do you want to uninstall USB Detect?\n\nYour configuration (macros) will be backed up to the Desktop.",
    "Désinstallation terminée": "Uninstall complete",
    "USB Detect a été désinstallé.\nVotre config a été sauvegardée sur le bureau.":
        "USB Detect has been uninstalled.\nYour config was backed up to the Desktop.",
    "USB Detect — Installation": "USB Detect — Installation",
    "Bienvenue ! USB Detect va s'installer dans :\n{dir}\n\nUn raccourci sera créé dans le menu Démarrer\net l'application apparaîtra dans vos programmes.\n\nContinuer ?":
        "Welcome! USB Detect will be installed in:\n{dir}\n\nA shortcut will be created in the Start menu\nand the application will appear in your programs.\n\nContinue?",
    "USB Detect — Mise à jour": "USB Detect — Update",
    "Une version plus récente va être installée :\n\n  Version installée : v{old}\n  Nouvelle version  : v{new}\n\nVotre configuration (macros) sera conservée.\n\nContinuer ?":
        "A newer version will be installed:\n\n  Installed version: v{old}\n  New version       : v{new}\n\nYour configuration (macros) will be preserved.\n\nContinue?",

    # ---- Changelog (Quoi de neuf) ----
    "Les boutons de test exécutent directement les actions, sans fenêtre de "
    "confirmation : les conditions sont ignorées pendant un test":
        "Test buttons now run the actions directly, with no confirmation dialog: "
        "conditions are ignored while testing",
    "Les boutons de test proposent d'exécuter les actions même si la "
    "condition du périphérique n'est pas remplie, au lieu de ne rien faire":
        "Test buttons now offer to run the actions even when the device "
        "condition is not met, instead of doing nothing",
    "Nouveau bouton « Tester maintenant » : exécute la commande et affiche "
    "son résultat, au lieu d'échouer en silence":
        "New “Test now” button: runs the command and shows its result, "
        "instead of failing silently",
    "Les actions ignorées à cause d'une condition invalide sont désormais "
    "signalées dans les logs":
        "Actions skipped because of an invalid condition are now reported in the logs",
    "Correction de l'erreur « Failed to load Python DLL » lors de la mise à jour":
        "Fixed the “Failed to load Python DLL” error during updates",
    "L'installateur ne dépend plus de l'environnement du programme qui le lance":
        "The installer no longer depends on the environment of the program launching it",
    "Les commandes sur plusieurs lignes fonctionnent enfin : nouvel éditeur "
    "multi-ligne, une commande par ligne":
        "Multi-line commands finally work: new multi-line editor, "
        "one command per line",
    "Les commandes cmd multi-lignes sont exécutées via un script temporaire":
        "Multi-line cmd commands are run through a temporary script",
    "Options avancées allégées : une seule ligne pour les conditions, "
    "au lieu de trois outils redondants":
        "Lighter advanced options: a single row for conditions, "
        "instead of three redundant tools",
    "Correction des actions « Commande shell » : les commandes PowerShell "
    "et cmd s'exécutent désormais correctement":
        "Fixed “Shell command” actions: PowerShell and cmd commands now run correctly",
    "Choix explicite de l'interpréteur (Auto, cmd ou PowerShell) pour chaque commande":
        "Explicit interpreter choice (Auto, cmd or PowerShell) for each command",
    "Les variables comme $env:USERPROFILE sont enfin correctement interprétées":
        "Variables such as $env:USERPROFILE are finally expanded correctly",
    "Les commandes exécutées sont journalisées (fini les échecs silencieux)":
        "Executed commands are now logged (no more silent failures)",
    "Refonte de la page de configuration des actions : cartes numérotées "
    "indiquant l'ordre d'exécution":
        "Redesigned action configuration page: numbered cards showing the execution order",
    "Délai et conditions désormais disponibles aussi pour les commandes":
        "Delay and conditions are now available for commands too",
    "Interface multilingue : français et anglais (Paramètres → Langue)":
        "Multilingual interface: French and English (Settings → Language)",
    "Détection automatique de la langue selon la locale du système":
        "Automatic language detection based on the system locale",
    "Support des commandes PowerShell comme action (détection auto et exécution via PowerShell)":
        "PowerShell commands supported as an action (auto-detection and execution via PowerShell)",
    "Installation automatique dans Program Files au premier lancement":
        "Automatic installation into Program Files on first launch",
    "Mise à jour intelligente : détecte et propose l'update si version plus récente":
        "Smart update: detects and offers the update if a newer version exists",
    "Nettoyage automatique du registre en cas de désinstallation manuelle":
        "Automatic registry cleanup in case of manual uninstall",
    "Les données (config, logs) sont stockées dans %APPDATA% (plus de problèmes de permissions)":
        "Data (config, logs) is stored in %APPDATA% (no more permission issues)",
    "Fenêtre 'Quoi de neuf' affichée après chaque mise à jour":
        "'What's new' window shown after each update",
    "Détection USB, HID et moniteurs en temps réel":
        "Real-time USB, HID and monitor detection",
    "Actions automatiques configurables (lancer/fermer des apps)":
        "Configurable automatic actions (launch/close apps)",
    "Démarrage avec Windows et mode system tray":
        "Start with Windows and system tray mode",
    "Vérification automatique des mises à jour GitHub":
        "Automatic GitHub update checking",
    "Conditions d'exécution (nombre de moniteurs, présence d'autres périphériques)":
        "Execution conditions (number of monitors, presence of other devices)",

    # ---- Notifications moteur (engine.py) ----
    "Connecté": "Connected",
    "Déconnecté": "Disconnected",
    "{name} détecté": "{name} detected",
    "{name} retiré": "{name} removed",

    # ---- Wizard : types d'action ----
    "▶  Lancer une app": "▶  Launch an app",
    "✕  Fermer une app": "✕  Close an app",
    "⌨  Commande shell": "⌨  Shell command",
    "📂  Ouvrir un fichier": "📂  Open a file",
    "▶  Lance un exécutable.\nIgnoré si le processus est déjà en cours.":
        "▶  Launches an executable.\nSkipped if the process is already running.",
    "✕  Ferme un processus Windows par son nom de fichier.":
        "✕  Closes a Windows process by its file name.",
    "⌨  Exécute une commande dans cmd / PowerShell.":
        "⌨  Runs a command in cmd / PowerShell.",
    "📂  Ouvre un fichier avec son application par défaut.":
        "📂  Opens a file with its default application.",
    "Type d'action": "Action type",
    "Processus (ex: opera.exe)": "Process (e.g. opera.exe)",
    "Nom exact du processus Windows (ex : opera.exe, Discord.exe)":
        "Exact Windows process name (e.g. opera.exe, Discord.exe)",
    "Chemin ou commande": "Path or command",
    "Chemin complet vers l'exécutable ou la commande à lancer":
        "Full path to the executable or command to run",
    "Parcourir pour choisir un fichier": "Browse to choose a file",
    "Options avancées : masquage forcé, délai, condition":
        "Advanced options: forced hiding, delay, condition",
    "Supprimer cette action": "Delete this action",
    "Démarre dans le systray\n(Discord, lghub, Razer, Signal RGB…)":
        "Starts in the system tray\n(Discord, lghub, Razer, Signal RGB…)",
    "Alternative à --minimized pour certaines apps":
        "Alternative to --minimized for some apps",
    "Mode silencieux (sans popup de bienvenue)":
        "Silent mode (no welcome popup)",
    "Paramètres supplémentaires…": "Additional parameters…",
    "Arguments passés à l'exécutable au lancement.\nCliquez sur un raccourci à gauche pour l'ajouter.":
        "Arguments passed to the executable at launch.\nClick a shortcut on the left to add it.",
    "Masquage forcé  (si --minimized absent)":
        "Forced hiding  (if --minimized is absent)",
    "Cache la fenêtre via Windows, puis envoie WM_CLOSE dès que\nle CPU du processus est idle (initialisation terminée).\nÀ utiliser uniquement si l'app ne supporte pas --minimized.\n\n⚠ Si l'icône systray ne répond plus, désactivez cette option.":
        "Hides the window via Windows, then sends WM_CLOSE as soon as\nthe process CPU is idle (initialization complete).\nUse only if the app does not support --minimized.\n\n⚠ If the tray icon stops responding, disable this option.",
    "Délai après (s) :": "Delay after (s):",
    "Pause après l'action avant la suivante (secondes)":
        "Pause after the action before the next one (seconds)",
    "Condition :": "Condition:",
    "Conditions séparées par &&  (toutes doivent être vraies)":
        "Conditions separated by &&  (all must be true)",
    "Toujours — utilisez les puces pour ajouter une condition":
        "Always — use the chips to add a condition",
    "Effacer la condition": "Clear the condition",
    "Conditions séparées par &&  (toutes doivent être vraies)\n"
    "  device_present:Nom   ce périphérique doit être connecté\n"
    "  device_absent:Nom    ce périphérique ne doit pas être connecté\n"
    "  monitors>=2          au moins 2 écrans (==, <=, >, < acceptés)":
        "Conditions separated by &&  (all must be true)\n"
        "  device_present:Name   this device must be connected\n"
        "  device_absent:Name    this device must not be connected\n"
        "  monitors>=2           at least 2 screens (==, <=, >, < accepted)",
    "Une commande par ligne — elles sont exécutées dans l'ordre.\n"
    "Exemple :\n"
    "  taskkill /f /im explorer.exe\n"
    "  start explorer.exe":
        "One command per line — they run in order.\n"
        "Example:\n"
        "  taskkill /f /im explorer.exe\n"
        "  start explorer.exe",
    "Une commande par ligne · exécutées via PowerShell":
        "One command per line · run via PowerShell",
    "Une commande par ligne · exécutées via cmd.exe":
        "One command per line · run via cmd.exe",
    "Une commande par ligne · interpréteur détecté automatiquement":
        "One command per line · interpreter detected automatically",
    "Périphérique présent": "Device present",
    "Périphérique absent": "Device absent",
    "Moniteurs ≥": "Monitors ≥",
    "Nom du périphérique": "Device name",
    "Ajouter la condition construite à la liste":
        "Add the built condition to the list",
    "＋ présent": "＋ present",
    "+ présent": "+ present",
    "Ajouter : si ce périphérique est connecté":
        "Add: if this device is connected",
    "＋ absent": "＋ absent",
    "+ absent": "+ absent",
    "Ajouter : si ce périphérique n'est PAS connecté":
        "Add: if this device is NOT connected",
    "＋ ≥2 écrans": "＋ ≥2 screens",
    "+ ≥2 écrans": "+ ≥2 screens",
    "Ajouter : si au moins 2 écrans sont connectés":
        "Add: if at least 2 screens are connected",
    "Aucune condition": "No condition",
    "Choisir un exécutable": "Choose an executable",
    "Exécutables (*.exe);;Tous les fichiers (*.*)":
        "Executables (*.exe);;All files (*.*)",
    "Processus à fermer  (ex : discord.exe)":
        "Process to close  (e.g. discord.exe)",
    "Processus  (ex : Discord.exe)": "Process  (e.g. Discord.exe)",
    "Chemin vers l'exécutable  (.exe ou raccourci .lnk)":
        "Path to the executable  (.exe or .lnk shortcut)",
    "Commande  (ex : taskkill /f /im app.exe)":
        "Command  (e.g. taskkill /f /im app.exe)",
    "Chemin vers le fichier à ouvrir": "Path to the file to open",

    # ---- Wizard : liste d'actions ----
    "＋  Ajouter une action": "＋  Add an action",
    "Ajouter une nouvelle action à cette liste":
        "Add a new action to this list",
    "Aucune action — cliquez sur « Ajouter une action ».":
        "No action yet — click “Add an action”.",
    "Ordre d'exécution de cette action": "Execution order of this action",
    "Les actions s'exécutent de haut en bas, dans l'ordre numéroté.":
        "Actions run from top to bottom, in the numbered order.",

    # ---- Wizard : test d'une commande ----
    "▷  Tester maintenant": "▷  Test now",
    "▷  Exécution…": "▷  Running…",
    "Exécute la commande immédiatement et affiche son résultat\n"
    "(code de retour et sorties), pour diagnostiquer un échec.":
        "Runs the command right away and shows its result\n"
        "(exit code and output), to diagnose a failure.",
    "Test de la commande": "Command test",
    "Saisissez d'abord une commande.": "Enter a command first.",
    "Interpréteur": "Interpreter",
    "Commande lancée": "Command launched",
    "La commande n'a pas pu être exécutée.": "The command could not be run.",
    "Commande exécutée avec succès (code 0).":
        "Command ran successfully (exit code 0).",
    "La commande s'est terminée avec le code {code}.":
        "The command exited with code {code}.",
    "Sortie": "Output",
    "Erreurs": "Errors",
    "(aucune sortie)": "(no output)",

    # ---- Wizard : interpréteur de commande ----
    "Auto": "Auto",
    "cmd": "cmd",
    "PowerShell": "PowerShell",
    "Interpréteur utilisé pour exécuter la commande.\n"
    "• cmd — commandes classiques (taskkill, start, shutdown…)\n"
    "• PowerShell — cmdlets et scripts .ps1 ; les variables\n"
    "  comme $env:USERPROFILE sont correctement interprétées.":
        "Interpreter used to run the command.\n"
        "• cmd — classic commands (taskkill, start, shutdown…)\n"
        "• PowerShell — cmdlets and .ps1 scripts; variables such as\n"
        "  $env:USERPROFILE are expanded correctly.",
    "Commande PowerShell  (ex : & \"$env:USERPROFILE\\script.ps1\")":
        "PowerShell command  (e.g. & \"$env:USERPROFILE\\script.ps1\")",
    "Commande cmd  (ex : taskkill /f /im app.exe)":
        "cmd command  (e.g. taskkill /f /im app.exe)",

    # ---- Wizard : fenêtre principale ----
    "Ajouter un périphérique": "Add a device",
    "Modifier le périphérique": "Edit the device",
    "Étape 1 / 2": "Step 1 / 2",
    "Étape 2 / 2": "Step 2 / 2",
    "Identification du périphérique": "Device identification",
    "Configuration des actions": "Action configuration",
    "← Précédent": "← Previous",
    "Retourner à l'étape d'identification":
        "Return to the identification step",
    "Suivant →": "Next →",
    "Passer à la configuration des actions":
        "Go to action configuration",
    "Fermer sans enregistrer": "Close without saving",
    "💾  Enregistrer": "💾  Save",
    "Enregistrer la configuration de ce périphérique":
        "Save this device's configuration",
    "Cliquez pour sélectionner un périphérique · Ctrl+clic pour en sélectionner plusieurs · Entrée pour valider":
        "Click to select a device · Ctrl+click to select several · Enter to confirm",
    "🔍  Filtrer les périphériques…": "🔍  Filter devices…",
    "Filtrer la liste par nom ou identifiant":
        "Filter the list by name or identifier",
    "⟳  Scanner": "⟳  Scan",
    "Actualiser la liste des périphériques détectés":
        "Refresh the list of detected devices",
    "🚫  Masquer la sélection": "🚫  Hide selection",
    "Masquer le ou les périphériques sélectionnés des futurs scans":
        "Hide the selected device(s) from future scans",
    "🤖  Masquer les internes": "🤖  Hide internal devices",
    "Masquer automatiquement les périphériques système/hubs/volumes internes":
        "Automatically hide system devices/hubs/internal volumes",
    "↺  Réinitialiser": "↺  Reset",
    "Afficher à nouveau tous les périphériques masqués":
        "Show all hidden devices again",
    "⟳  Scan en cours…": "⟳  Scanning…",
    "  ou saisir manuellement  ": "  or enter manually  ",
    "ex: VID_046D&PID_0AB7&MI  ou  Razer Tartarus":
        "e.g. VID_046D&PID_0AB7&MI  or  Razer Tartarus",
    "Fragment unique de l'identifiant Windows du périphérique":
        "Unique fragment of the device's Windows identifier",
    "Identifiant :": "Identifier:",
    "Mode de correspondance pour reconnaître le périphérique":
        "Matching mode used to recognize the device",
    "Correspondance :": "Matching:",
    "✔ Vrai si l'identifiant contient ce texte (recommandé)":
        "✔ True if the identifier contains this text (recommended)",
    "✔ Vrai si l'identifiant correspond exactement à une ligne":
        "✔ True if the identifier exactly matches a line",
    "✔ Vrai si l'identifiant correspond à l'expression régulière":
        "✔ True if the identifier matches the regular expression",
    "Conditions d'exécution": "Execution conditions",
    "Définissez des conditions qui doivent être remplies pour que les actions\nde ce périphérique s'exécutent (connexion et déconnexion).":
        "Define conditions that must be met for this device's actions\nto run (connection and disconnection).",
    "Les actions ne s'exécuteront que si toutes les conditions sont vraies.\nExemple : bloquer les actions si un autre périphérique spécifique est présent.":
        "Actions will run only if all conditions are true.\nExample: block actions if another specific device is present.",
    "device_present:Nom  &&  device_absent:Autre":
        "device_present:Name  &&  device_absent:Other",
    "device_present:Nom  &&  device_absent:Autre  &&  monitors>=2":
        "device_present:Name  &&  device_absent:Other  &&  monitors>=2",
    "Conditions séparées par &&  (toutes doivent être vraies)\n  device_present:Nom  ->  ce périphérique DOIT être connecté\n  device_absent:Nom   ->  ce périphérique NE DOIT PAS être connecté":
        "Conditions separated by &&  (all must be true)\n  device_present:Name  ->  this device MUST be connected\n  device_absent:Name   ->  this device must NOT be connected",
    "Nom :": "Name:",
    "ex : Clavier Corsair, Manette, Micro Logitech…":
        "e.g. Corsair Keyboard, Gamepad, Logitech Mic…",
    "Nom affiché dans la liste principale de l'application":
        "Name shown in the application's main list",
    "Demander confirmation avant de fermer les applications":
        "Ask for confirmation before closing applications",
    "Si coché, une boîte de dialogue s'affichera lors de la déconnexion\navant d'exécuter les actions de fermeture.":
        "If checked, a dialog will appear on disconnection\nbefore running the close actions.",
    "Options :": "Options:",
    "⚡  Actions à la CONNEXION": "⚡  Actions on CONNECTION",
    "Actions exécutées automatiquement quand ce périphérique est branché":
        "Actions run automatically when this device is plugged in",
    "✖  Actions à la DÉCONNEXION": "✖  Actions on DISCONNECTION",
    "Actions exécutées automatiquement quand ce périphérique est retiré":
        "Actions run automatically when this device is removed",
    "Veuillez renseigner un identifiant de périphérique.":
        "Please enter a device identifier.",
    "Nouveau périphérique": "New device",
    "{n} périphérique détecté (USB, HID, HDMI){hidden}":
        "{n} device detected (USB, HID, HDMI){hidden}",
    "{n} périphériques détectés (USB, HID, HDMI){hidden}":
        "{n} devices detected (USB, HID, HDMI){hidden}",
    "  ·  {n} masqué": "  ·  {n} hidden",
    "  ·  {n} masqués": "  ·  {n} hidden",
    "Aucune condition": "No condition",
}
