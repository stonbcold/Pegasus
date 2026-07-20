# pegasus_common.py
#!/usr/bin/env python3
"""Fonctions partagées entre le serveur et l'agent"""

import os
import sys
import platform
import subprocess
import datetime
import json

try:
    import psutil
except ImportError:
    print("Module manquant: psutil")
    print("Installe-le avec: pip install psutil")
    sys.exit(1)

LOG_FILE = "pegasus_log.txt"

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# --- TOUTES TES FONCTIONS EXISTANTES ICI ---
# system_info(), cpu_ram_status(), disk_usage(), etc.
# (je les recopie telles quelles)

# --- NOUVEAU : un dispatcher pour appeler les fonctions par leur nom ---
def execute_action(action_name, params=None):
    """
    Exécute une action par son nom et retourne le résultat formaté.
    Utilisé par l'agent pour exécuter les commandes reçues du serveur.
    """
    actions = {
        "system_info": system_info,
        "cpu_ram": cpu_ram_status,
        "disk_usage": disk_usage,
        "network_info": network_info,
        "list_processes": list_processes,
        "kill_process": kill_process,
        "startup_programs": list_startup_programs,
        "screenshot": take_screenshot,
        "installed_programs": list_installed_programs,
        "open_explorer": open_file_explorer,
        "list_directory": list_directory,
        "search_file": search_file,
        "battery": check_battery,
        "restart": restart_pc,
        "shutdown": shutdown_pc,
    }
    
    # Récupère la fonction
    func = actions.get(action_name)
    if not func:
        return {"error": f"Action inconnue: {action_name}"}
    
    # Exécute avec les paramètres si besoin
    if params and action_name == "kill_process":
        # kill_process attend un PID saisi par l'utilisateur, on le contourne
        return kill_process_with_pid(params.get("pid"))
    elif params and action_name == "list_directory":
        return list_directory_path(params.get("path", "."))
    elif params and action_name == "search_file":
        return search_file_name(params.get("name"), params.get("root", r"C:\Users"))
    elif params and action_name == "open_explorer":
        return open_explorer_path(params.get("path", "."))
    else:
        # Pour les fonctions sans paramètres, on capture leur sortie
        return capture_output(func)

def capture_output(func):
    """Capture la sortie console d'une fonction pour l'envoyer au serveur"""
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        func()
    return {"output": f.getvalue()}

# --- VERSIONS ADAPTÉES POUR LES FONCTIONS AVEC PARAMÈTRES ---

def kill_process_with_pid(pid):
    """Version de kill_process qui prend un PID directement"""
    if not pid:
        return {"error": "PID manquant"}
    try:
        p = psutil.Process(int(pid))
        name = p.name()
        p.terminate()
        log_event(f"Processus arrete: {name} (PID {pid})")
        return {"output": f"Processus {name} (PID {pid}) arrete."}
    except Exception as e:
        return {"error": str(e)}

def list_directory_path(path):
    """Version de list_directory qui prend un chemin directement"""
    try:
        result = []
        for entry in os.scandir(path):
            kind = "DIR " if entry.is_dir() else "FILE"
            size = entry.stat().st_size if entry.is_file() else ""
            result.append(f"[{kind}] {entry.name}  {size}")
        return {"output": "\n".join(result)}
    except Exception as e:
        return {"error": str(e)}

def search_file_name(name, root):
    """Version de search_file qui prend nom et racine directement"""
    if not name:
        return {"error": "Nom de fichier manquant"}
    found = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if name.lower() in f.lower():
                found.append(os.path.join(dirpath, f))
                if len(found) >= 50:
                    break
        if len(found) >= 50:
            break
    return {"output": "\n".join(found) + f"\n\n{len(found)} resultat(s) (limite a 50)."}

def open_explorer_path(path):
    """Version d'open_explorer qui prend un chemin directement"""
    subprocess.run(["explorer", path])
    return {"output": f"Explorateur ouvert sur: {path}"}