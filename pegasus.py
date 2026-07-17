#!/usr/bin/env python3
"""
PEGASUS - Windows System Management Tool
Outil personnel de gestion et de diagnostic pour TON PC Windows,
lance et utilise localement, sur la machine sur laquelle il tourne.

Necessite: pip install psutil pillow
"""

import os
import sys
import platform
import subprocess
import datetime

# Assure l'affichage correct des caracteres Unicode (banniere, cadres)
# quel que soit le terminal ou la page de code du PC.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import psutil
except ImportError:
    print("Module manquant: psutil")
    print("Installe-le avec: pip install psutil")
    sys.exit(1)

BANNER = r"""
 ██████╗ ███████╗ ██████╗  █████╗ ███████╗██╗   ██╗███████╗
 ██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝██║   ██║██╔════╝
 ██████╔╝█████╗  ██║  ███╗███████║███████╗██║   ██║███████╗
 ██╔═══╝ ██╔══╝  ██║   ██║██╔══██║╚════██║██║   ██║╚════██║
 ██║     ███████╗╚██████╔╝██║  ██║███████║╚██████╔╝███████╗
 ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
              Windows System Management Tool (local)
"""

LOG_FILE = "pegasus_log.txt"


def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def system_info():
    print("\n--- Informations systeme ---")
    print(f"OS            : {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Machine       : {platform.node()}")
    print(f"Processeur    : {platform.processor()}")
    print(f"Architecture  : {platform.machine()}")
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    print(f"Demarre depuis: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")


def cpu_ram_status():
    print("\n--- CPU / RAM ---")
    print(f"Utilisation CPU : {psutil.cpu_percent(interval=1)} %")
    mem = psutil.virtual_memory()
    print(f"RAM utilisee    : {mem.percent} % ({mem.used // (1024**2)} Mo / {mem.total // (1024**2)} Mo)")


def disk_usage():
    print("\n--- Disques ---")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            print(f"{part.device:<10} {usage.used // (1024**3):>4} Go / {usage.total // (1024**3):>4} Go  ({usage.percent}% utilise)")
        except PermissionError:
            continue


def network_info():
    print("\n--- Reseau ---")
    stats = psutil.net_if_addrs()
    for iface, addrs in stats.items():
        print(f"\n{iface}:")
        for addr in addrs:
            fam = addr.family.name if hasattr(addr.family, "name") else addr.family
            print(f"   {fam}: {addr.address}")


def list_processes():
    print("\n--- Processus en cours (top 20 par RAM) ---")
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            procs.append((p.info["pid"], p.info["name"], p.info["memory_info"].rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x[2], reverse=True)
    print(f"{'PID':<8}{'Nom':<30}{'RAM (Mo)'}")
    for pid, name, mem in procs[:20]:
        print(f"{pid:<8}{name:<30}{mem // (1024**2)}")


def kill_process():
    pid = input("PID du processus a arreter: ").strip()
    try:
        p = psutil.Process(int(pid))
        name = p.name()
        confirm = input(f"Confirmer l'arret de '{name}' (PID {pid}) ? (o/n): ").strip().lower()
        if confirm == "o":
            p.terminate()
            log_event(f"Processus arrete: {name} (PID {pid})")
            print("Processus arrete.")
    except Exception as e:
        print(f"Erreur: {e}")


def list_startup_programs():
    print("\n--- Programmes au demarrage ---")
    result = subprocess.run(
        ["wmic", "startup", "get", "Caption,Command"],
        capture_output=True, text=True
    )
    print(result.stdout)


def take_screenshot():
    try:
        from PIL import ImageGrab
    except ImportError:
        print("Module manquant: pillow. Installe-le avec: pip install pillow")
        return
    img = ImageGrab.grab()
    filename = f"screen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(filename)
    log_event(f"Capture d'ecran: {filename}")
    print(f"Capture sauvegardee: {filename}")


def list_installed_programs():
    print("\n--- Programmes installes ---")
    result = subprocess.run(
        ["wmic", "product", "get", "name"],
        capture_output=True, text=True
    )
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and l.strip() != "Name"]
    with open("installed_programs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{len(lines)} programmes trouves. Sauvegarde dans installed_programs.txt")


def open_file_explorer():
    path = input("Chemin a ouvrir dans l'explorateur (defaut: dossier courant): ").strip() or "."
    subprocess.run(["explorer", path])


def list_directory():
    path = input("Chemin a lister (defaut: dossier courant): ").strip() or "."
    try:
        for entry in os.scandir(path):
            kind = "DIR " if entry.is_dir() else "FILE"
            size = entry.stat().st_size if entry.is_file() else ""
            print(f"[{kind}] {entry.name}  {size}")
    except Exception as e:
        print(f"Erreur: {e}")


def search_file():
    name = input("Nom (partiel) du fichier a chercher: ").strip().lower()
    root = input("Dossier de depart (defaut: C:\\Users): ").strip() or r"C:\Users"
    print("Recherche en cours...")
    found = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if name in f.lower():
                found.append(os.path.join(dirpath, f))
                if len(found) >= 50:
                    break
        if len(found) >= 50:
            break
    for f in found:
        print(f)
    print(f"\n{len(found)} resultat(s) (limite a 50).")


def check_battery():
    battery = psutil.sensors_battery()
    if battery is None:
        print("Pas de batterie detectee (PC fixe ?).")
        return
    print(f"\nBatterie : {battery.percent}%  |  Branche : {'oui' if battery.power_plugged else 'non'}")


def restart_pc():
    confirm = input("Redemarrer le PC maintenant ? (o/n): ").strip().lower()
    if confirm == "o":
        log_event("Redemarrage demande")
        os.system("shutdown /r /t 5")
        print("Redemarrage dans 5 secondes.")


def shutdown_pc():
    confirm = input("Eteindre le PC maintenant ? (o/n): ").strip().lower()
    if confirm == "o":
        log_event("Extinction demandee")
        os.system("shutdown /s /t 5")
        print("Extinction dans 5 secondes.")


def show_menu():
    print(BANNER)
    print("=" * 60)
    print(" [1]  Infos systeme              [2]  CPU / RAM")
    print(" [3]  Etat des disques            [4]  Infos reseau")
    print(" [5]  Liste des processus         [6]  Arreter un processus")
    print(" [7]  Programmes au demarrage     [8]  Capture d'ecran")
    print(" [9]  Programmes installes        [10] Ouvrir l'explorateur")
    print(" [11] Lister un dossier           [12] Chercher un fichier")
    print(" [13] Etat de la batterie         [14] Redemarrer le PC")
    print(" [15] Eteindre le PC")
    print(" [q]  Quitter")
    print("=" * 60)


ACTIONS = {
    "1": system_info,
    "2": cpu_ram_status,
    "3": disk_usage,
    "4": network_info,
    "5": list_processes,
    "6": kill_process,
    "7": list_startup_programs,
    "8": take_screenshot,
    "9": list_installed_programs,
    "10": open_file_explorer,
    "11": list_directory,
    "12": search_file,
    "13": check_battery,
    "14": restart_pc,
    "15": shutdown_pc,
}


def main():
    if platform.system() != "Windows":
        print("Attention: ce script est concu pour Windows. Certaines fonctions ne marcheront pas ici.")
    log_event("Session demarree")
    while True:
        show_menu()
        choice = input("\nChoix: ").strip().lower()
        if choice == "q":
            log_event("Session terminee")
            print("A bientot.")
            break
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except KeyboardInterrupt:
                print("\nInterrompu.")
            except Exception as e:
                print(f"Erreur: {e}")
        else:
            print("Choix invalide.")
        input("\nAppuie sur Entree pour continuer...")


if __name__ == "__main__":
    main()
