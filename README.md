# PEGASUS

```
 ██████╗ ███████╗ ██████╗  █████╗ ███████╗██╗   ██╗███████╗
 ██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝██║   ██║██╔════╝
 ██████╔╝█████╗  ██║  ███╗███████║███████╗██║   ██║███████╗
 ██╔═══╝ ██╔══╝  ██║   ██║██╔══██║╚════██║██║   ██║╚════██║
 ██║     ███████╗╚██████╔╝██║  ██║███████║╚██████╔╝███████╗
 ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
```

**Outil personnel de gestion et de diagnostic pour PC Windows.**
Un menu interactif en ligne de commande qui regroupe les informations et les
actions les plus utiles pour surveiller et gérer *ta propre* machine Windows,
en local, sur le PC où le script tourne.

---

## Fonctionnalités

| # | Fonction | Description |
|---|----------|-------------|
| 1  | Infos système           | OS, machine, processeur, architecture, heure de démarrage |
| 2  | CPU / RAM               | Utilisation processeur et mémoire en temps réel |
| 3  | État des disques        | Espace utilisé / total par partition |
| 4  | Infos réseau            | Interfaces et adresses (IPv4 / IPv6 / MAC) |
| 5  | Liste des processus     | Top 20 des processus par consommation mémoire |
| 6  | Arrêter un processus    | Termine un processus par son PID (avec confirmation) |
| 7  | Programmes au démarrage | Liste les programmes lancés au démarrage de Windows |
| 8  | Capture d'écran         | Enregistre une capture d'écran en PNG |
| 9  | Programmes installés    | Exporte la liste des logiciels installés |
| 10 | Ouvrir l'explorateur    | Ouvre un dossier dans l'explorateur Windows |
| 11 | Lister un dossier       | Affiche le contenu d'un répertoire |
| 12 | Chercher un fichier     | Recherche récursive d'un fichier par nom |
| 13 | État de la batterie     | Niveau et état de charge (ordinateurs portables) |
| 14 | Redémarrer le PC        | Redémarre la machine (avec confirmation) |
| 15 | Éteindre le PC          | Éteint la machine (avec confirmation) |

---

## Installation

Nécessite **Python 3** et les dépendances suivantes :

```bash
pip install psutil pillow
```

- `psutil` — informations système, processus, réseau, batterie
- `pillow` — captures d'écran (fonction 8)

---

## Utilisation

```bash
python pegasus.py
```

Le menu s'affiche : tape le numéro de l'action voulue puis `Entrée`.
Tape `q` pour quitter.

<!-- 📸 AJOUTE TA PHOTO ICI — capture d'une fonction en action (ex : CPU/RAM ou liste des processus) -->

*(Emplacement réservé pour une capture d'une fonction en cours d'utilisation)*

---

## Notes

- Les actions sensibles (arrêt de processus, redémarrage, extinction) demandent
  une **confirmation** avant de s'exécuter.
- Un journal des sessions et des actions est écrit dans `pegasus_log.txt`.
- Conçu pour **Windows**. Sur un autre système, certaines fonctions
  (démarrage, programmes installés, extinction…) ne fonctionneront pas.
- Outil destiné à un usage **local et personnel**, sur ta propre machine.

---

## Fichiers générés

| Fichier | Contenu |
|---------|---------|
| `pegasus_log.txt`         | Journal des sessions et des actions |
| `screen_*.png`            | Captures d'écran (fonction 8) |
| `installed_programs.txt`  | Liste des programmes installés (fonction 9) |
