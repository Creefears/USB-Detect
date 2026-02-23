# 🔌 USB Detect

> [!CAUTION]
> ## ⚠️ IMPORTANT — AVERTISSEMENT
> Ce logiciel a été conçu et généré exclusivement par une intelligence artificielle.
> Il est fourni **tel quel**, sans garantie de fonctionnement parfait, de sécurité ou d’adéquation à un usage en production.
> Utilisez-le à vos propres risques et testez-le soigneusement avant tout déploiement.

---

## 📖 Présentation
**USB Detect** est un outil léger permettant de surveiller en temps réel la connexion et la déconnexion de périphériques USB sous Windows.

Le programme peut :
* **Détecter** automatiquement les périphériques USB.
* **Enregistrer** les événements (connexion / déconnexion).
* **Afficher** les informations détaillées des périphériques.
* **Déclencher** des actions personnalisées.
* **Ignorer** les actions si certains périphériques sont présents (liste de blocage).

Il est conçu pour fonctionner en arrière-plan avec une consommation minimale de ressources.

---

## ✨ Fonctionnalités principales
* 🔍 **Surveillance USB** en temps réel.
* 📝 **Journalisation** complète des événements.
* ⚙️ **Actions automatiques** configurables.
* 🚫 **Liste de périphériques bloquants**.
* 🪶 **Script léger** (Python).
* 🧩 **Configuration simple** via JSON.

---

## 🗂️ Structure du projet
* **engine.py** : Moteur principal
* **config.json** : Configuration
* **logger.py** : Gestion des logs
* **utils.py** : Fonctions utilitaires
* **README.md** : Documentation

---

## ⚙️ Prérequis
* Windows 10/11
* Python 3.10+
* Dépendances Python : `pip install -r requirements.txt`

---

## 🚀 Installation
1. **Cloner le dépôt** :
   `git clone https://github.com/votre-repo/USB-Detect.git`
2. **Entrer dans le dossier** :
   `cd USB-Detect`
3. **Lancer le programme** :
   `python engine.py`

---

## 🧪 Fonctionnement
Le logiciel surveille le système en continu. Lorsqu’un périphérique USB est :
* ✅ **Connecté** : événement enregistré.
* ❌ **Déconnecté** : événement enregistré.

---

## 🚫 Périphériques bloquants
Il est possible d’empêcher l’exécution des actions si certains périphériques sont présents.
Dans le fichier `config.json`, remplissez la liste `blocked_devices`.

**🔎 Comportement :**
Si un périphérique de cette liste est détecté, les actions automatiques sont ignorées et un message est inscrit dans les logs. La correspondance est partielle et insensible à la casse.

---

## 📝 Logs
Le programme enregistre : le nom du périphérique, le type, la date/heure et l'état. Cela permet un audit simple des connexions.

---

## 🧩 Personnalisation
Toute la configuration (périphériques surveillés, actions, niveau de log) se fait directement dans le fichier `config.json`.

---

## ⚠️ Limitations connues
* Conçu principalement pour Windows.
* Dépend de la détection système USB.
* Non testé en environnement critique.

---

## 🛡️ Avertissement de sécurité
Ce projet est fourni à des fins pédagogiques. Avant toute utilisation en production, testez en environnement contrôlé et validez les actions automatiques.

---

## 🤖 Crédit
Ce logiciel a été entièrement conçu et généré par intelligence artificielle, puis testé et intégré par l’utilisateur.
