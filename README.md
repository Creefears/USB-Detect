🔌 USB Detect

⚠️ IMPORTANT — AVERTISSEMENT
Ce logiciel a été conçu et généré exclusivement par une intelligence artificielle.
Il est fourni tel quel, sans garantie de fonctionnement parfait, de sécurité ou d’adéquation à un usage en production.
Utilisez-le à vos propres risques et testez-le soigneusement avant tout déploiement.

📖 Présentation

USB Detect est un outil léger permettant de surveiller en temps réel la connexion et la déconnexion de périphériques USB sous Windows.

Le programme peut :

détecter automatiquement les périphériques USB

enregistrer les événements (connexion / déconnexion)

afficher les informations des périphériques

déclencher des actions personnalisées

ignorer les actions si certains périphériques sont présents (liste de blocage)

Il est conçu pour fonctionner en arrière-plan avec une consommation minimale de ressources.

✨ Fonctionnalités principales

🔍 Surveillance USB en temps réel

📝 Journalisation des événements

⚙️ Actions automatiques configurables

🚫 Liste de périphériques bloquants

🪶 Script léger (Python)

🧩 Configuration simple via JSON

🗂️ Structure du projet
USB-Detect/
├── engine.py          # Moteur principal
├── config.json        # Configuration
├── logger.py          # Gestion des logs
├── utils.py           # Fonctions utilitaires
└── README.md
⚙️ Prérequis

Windows 10/11

Python 3.10+

Dépendances Python

Installez les dépendances si nécessaire :

pip install -r requirements.txt

(si le fichier requirements.txt est présent)

🚀 Installation

Cloner le dépôt :

git clone https://github.com/votre-repo/USB-Detect.git
cd USB-Detect

Vérifier la configuration dans config.json

Lancer le programme :

python engine.py
🧪 Fonctionnement

Le logiciel surveille le système en continu.

Lorsqu’un périphérique USB est :

✅ connecté → événement enregistré

❌ déconnecté → événement enregistré

Selon la configuration, des actions peuvent être exécutées automatiquement.

🚫 Périphériques bloquants

Il est possible d’empêcher l’exécution des actions si certains périphériques sont présents.

Dans config.json :

{
  "general": {
    "blocked_devices": [
      "VID_XXXX&PID_YYYY",
      "USB Storage Device"
    ]
  }
}
🔎 Comportement

Si un périphérique de cette liste est détecté :

les actions automatiques sont ignorées

un message est inscrit dans les logs

La correspondance est partielle et insensible à la casse.

📝 Logs

Le programme enregistre :

nom du périphérique

type

date et heure

état (connecté / déconnecté)

Les logs permettent un audit simple des connexions USB.

🧩 Personnalisation

Vous pouvez adapter facilement :

les périphériques surveillés

les actions exécutées

les périphériques bloquants

le niveau de log

Toute la configuration se fait dans config.json.

⚠️ Limitations connues

conçu principalement pour Windows

dépend de la détection système USB

non testé en environnement critique

peut nécessiter des ajustements selon le matériel

🛡️ Avertissement de sécurité

Ce projet est fourni à des fins pédagogiques et expérimentales.

Avant toute utilisation en production :

testez en environnement contrôlé

vérifiez les logs

validez les actions automatiques

📜 Licence

À définir par le mainteneur du dépôt.

🤖 Crédit

Ce logiciel a été entièrement conçu et généré par intelligence artificielle, puis testé et intégré par l’utilisateur.

Bon test ! 🚀
