# USB Detect

> [!CAUTION]
> ## IMPORTANT — AVERTISSEMENT
> Ce logiciel a été conçu et généré exclusivement par une intelligence artificielle.
> Il est fourni **tel quel**, sans garantie de fonctionnement parfait, de sécurité ou d'adéquation à un usage en production.
> Utilisez-le à vos propres risques et testez-le soigneusement avant tout déploiement.

---

## Présentation
**USB Detect** est un outil léger permettant de surveiller en temps réel la connexion et la déconnexion de périphériques USB sous Windows.

Le programme peut :
* **Détecter** automatiquement les périphériques USB, HID et moniteurs.
* **Enregistrer** les événements (connexion / déconnexion).
* **Déclencher** des actions personnalisées (lancer/fermer des applications, commandes).
* **Activer/Désactiver** individuellement chaque macro sans le supprimer.
* **Démarrer avec Windows** et se lancer en arrière-plan dans le system tray.
* **Vérifier les mises à jour** GitHub automatiquement.

Il est conçu pour fonctionner en arrière-plan avec une consommation minimale de ressources.

---

## Fonctionnalités principales
* **Surveillance USB** en temps réel via WMI.
* **Journalisation** complète des événements.
* **Actions automatiques** configurables (lancement, fermeture, commandes).
* **Conditions d'exécution** (nombre de moniteurs, présence d'autres périphériques).
* **Activation/Désactivation** de chaque macro individuellement.
* **Démarrage automatique** avec Windows (option dans les paramètres).
* **Mode system tray** — se minimise dans la barre des tâches.
* **Mise à jour automatique** — notification et lien direct vers GitHub.
* **Configuration préservée** lors des mises à jour.

---

## Structure du projet
* **main.py** : Interface graphique PyQt6
* **engine.py** : Moteur de détection et d'actions
* **wizard.py** : Assistant d'ajout/édition de périphériques
* **build.py** : Script de build pour générer l'exécutable
* **config.example.json** : Configuration par défaut (modèle)
* **config.json** : Configuration utilisateur (créé au premier lancement)
* **usb_detect.ico** : Icône de l'application

---

## Prérequis
* Windows 10/11
* Python 3.10+
* Dépendances Python : `pip install -r requirements.txt`

---

## Installation

### Depuis les sources
1. **Cloner le dépôt** :
   ```
   git clone https://github.com/Creefears/USB-Detect.git
   ```
2. **Entrer dans le dossier** :
   ```
   cd USB-Detect
   ```
3. **Installer les dépendances** :
   ```
   pip install -r requirements.txt
   ```
4. **Lancer le programme** :
   ```
   pythonw main.py
   ```

### Générer l'exécutable (.exe)
```
pip install pyinstaller Pillow
python build.py
```
L'exécutable sera dans le dossier `dist/`.

---

## Configuration

La configuration se fait via l'interface graphique ou le fichier `config.json`.

Au premier lancement, `config.json` est créé automatiquement à partir de `config.example.json`.

**Important** : `config.json` est ignoré par Git pour préserver vos macros lors des mises à jour.

### Paramètres disponibles
| Paramètre | Description |
|---|---|
| `start_with_windows` | Lancer au démarrage de Windows |
| `start_in_tray` | Démarrer en arrière-plan (system tray) |
| `start_minimized` | Démarrer la fenêtre minimisée |
| `notifications_enabled` | Activer les notifications |
| `log_enabled` | Activer les logs |

---

## Fonctionnement
Le logiciel surveille le système toutes les 5 secondes. Lorsqu'un périphérique USB est :
* **Connecté** : les actions de connexion sont exécutées.
* **Déconnecté** : les actions de déconnexion sont exécutées.

Chaque macro peut être **activé ou désactivé** individuellement via le bouton ON/OFF.

---

## Mise à jour
USB Detect vérifie automatiquement les mises à jour GitHub au lancement. Si une nouvelle version est disponible, une bannière s'affiche avec un bouton pour accéder à la page de téléchargement.

---

## Limitations connues
* Conçu principalement pour Windows.
* Dépend de la détection système USB via WMI.
* Non testé en environnement critique.

---

## Avertissement de sécurité
Ce projet est fourni à des fins pédagogiques. Avant toute utilisation en production, testez en environnement contrôlé et validez les actions automatiques.

---

## Crédit
Ce logiciel a été entièrement conçu et généré par intelligence artificielle, puis testé et intégré par l'utilisateur.
