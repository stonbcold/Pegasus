# pegasus_server.py
#!/usr/bin/env python3
"""PEGASUS - Version Serveur (contrôle à distance)"""

import socket
import json
import threading
import datetime
import sys
import platform

# Réimporte la bannière et les constantes
BANNER = r"""
 ██████╗ ███████╗ ██████╗  █████╗ ███████╗██╗   ██╗███████╗
 ██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝██║   ██║██╔════╝
 ██████╔╝█████╗  ██║  ███╗███████║███████╗██║   ██║███████╗
 ██╔═══╝ ██╔══╝  ██║   ██║██╔══██║╚════██║██║   ██║╚════██║
 ██║     ███████╗╚██████╔╝██║  ██║███████║╚██████╔╝███████╗
 ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
              SERVEUR - Contrôle à distance
"""

class PegasusServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.clients = {}  # {client_socket: (addr, nom)}
        self.server = None
        self.running = False
        
    def start(self):
        """Démarre le serveur"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.running = True
        
        print(BANNER)
        print("=" * 60)
        print(f"🚀 Serveur démarré sur {self.host}:{self.port}")
        print("📡 En attente de connexions...")
        print("=" * 60)
        
        while self.running:
            try:
                client, addr = self.server.accept()
                print(f"\n✅ Nouvel agent connecté : {addr}")
                # Demande à l'agent de s'identifier
                client.send(json.dumps({"type": "identify"}).encode())
                try:
                    data = client.recv(1024).decode()
                    info = json.loads(data)
                    nom = info.get("nom", f"Agent-{addr[1]}")
                    self.clients[client] = (addr, nom)
                    print(f"   Identifié : {nom}")
                except:
                    self.clients[client] = (addr, f"Agent-{addr[1]}")
                
                # Lance un thread pour gérer ce client
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"Erreur: {e}")
    
    def handle_client(self, client):
        """Gère un client en arrière-plan"""
        addr, nom = self.clients.get(client, ("Inconnu", "Inconnu"))
        try:
            while True:
                # On écoute juste les messages de l'agent (pour l'instant, il n'envoie que des réponses)
                # On pourrait ajouter un keepalive plus tard
                pass
        except:
            pass
        finally:
            if client in self.clients:
                print(f"❌ Agent déconnecté : {nom} ({addr})")
                del self.clients[client]
            try:
                client.close()
            except:
                pass
    
    def send_command(self, client, action, params=None):
        """Envoie une commande à un agent et attend la réponse"""
        commande = {"action": action}
        if params:
            commande["params"] = params
        
        try:
            client.send(json.dumps(commande).encode())
            # Attend la réponse
            data = client.recv(4096).decode()
            return json.loads(data)
        except Exception as e:
            return {"error": f"Erreur de communication: {e}"}
    
    def show_menu(self):
        """Affiche le menu (adapté du tien)"""
        print("\n" + "=" * 60)
        print(" [1]  Infos système              [2]  CPU / RAM")
        print(" [3]  État des disques            [4]  Infos réseau")
        print(" [5]  Liste des processus         [6]  Arrêter un processus")
        print(" [7]  Programmes au démarrage     [8]  Capture d'écran")
        print(" [9]  Programmes installés        [10] Ouvrir l'explorateur")
        print(" [11] Lister un dossier           [12] Chercher un fichier")
        print(" [13] État de la batterie         [14] Redémarrer le PC")
        print(" [15] Éteindre le PC")
        print(" [l]  Liste des agents connectés")
        print(" [q]  Quitter")
        print("=" * 60)
    
    def get_target(self):
        """Demande à l'utilisateur de choisir un agent cible"""
        if not self.clients:
            print("❌ Aucun agent connecté !")
            return None
        
        print("\n📡 Agents disponibles :")
        clients_list = list(self.clients.items())
        for i, (client, (addr, nom)) in enumerate(clients_list):
            print(f"  [{i+1}] {nom} ({addr[0]}:{addr[1]})")
        
        try:
            choix = int(input("Choisis l'agent (numéro) : ")) - 1
            if 0 <= choix < len(clients_list):
                return clients_list[choix][0]
            else:
                print("❌ Choix invalide")
                return None
        except ValueError:
            print("❌ Entrée invalide")
            return None
    
    def run(self):
        """Boucle principale du serveur"""
        ACTIONS = {
            "1": "system_info",
            "2": "cpu_ram",
            "3": "disk_usage",
            "4": "network_info",
            "5": "list_processes",
            "6": "kill_process",
            "7": "startup_programs",
            "8": "screenshot",
            "9": "installed_programs",
            "10": "open_explorer",
            "11": "list_directory",
            "12": "search_file",
            "13": "battery",
            "14": "restart",
            "15": "shutdown",
        }
        
        while True:
            self.show_menu()
            choice = input("\nChoix: ").strip().lower()
            
            if choice == "q":
                print("Arrêt du serveur...")
                self.running = False
                self.server.close()
                break
            
            if choice == "l":
                if not self.clients:
                    print("📡 Aucun agent connecté.")
                else:
                    print(f"\n📡 {len(self.clients)} agent(s) connecté(s) :")
                    for client, (addr, nom) in self.clients.items():
                        print(f"   • {nom} ({addr[0]}:{addr[1]})")
                input("\nAppuie sur Entrée pour continuer...")
                continue
            
            if choice not in ACTIONS:
                print("❌ Choix invalide.")
                input("\nAppuie sur Entrée pour continuer...")
                continue
            
            # Sélectionne la cible
            target = self.get_target()
            if not target:
                input("\nAppuie sur Entrée pour continuer...")
                continue
            
            action = ACTIONS[choice]
            params = None
            
            # Gestion des paramètres pour certaines actions
            if choice == "6":  # kill_process
                pid = input("PID du processus à arrêter: ").strip()
                if not pid:
                    print("❌ PID requis")
                    input("\nAppuie sur Entrée pour continuer...")
                    continue
                params = {"pid": int(pid)}
            elif choice == "10":  # open_explorer
                path = input("Chemin à ouvrir (défaut: .): ").strip() or "."
                params = {"path": path}
            elif choice == "11":  # list_directory
                path = input("Chemin à lister (défaut: .): ").strip() or "."
                params = {"path": path}
            elif choice == "12":  # search_file
                name = input("Nom (partiel) du fichier: ").strip()
                if not name:
                    print("❌ Nom requis")
                    input("\nAppuie sur Entrée pour continuer...")
                    continue
                root = input("Dossier de départ (défaut: C:\\Users): ").strip() or r"C:\Users"
                params = {"name": name, "root": root}
            
            # Envoie la commande
            print(f"\n⏳ Envoi de la commande à l'agent...")
            reponse = self.send_command(target, action, params)
            
            # Affiche le résultat
            if "error" in reponse:
                print(f"❌ Erreur: {reponse['error']}")
            elif "output" in reponse:
                print(reponse["output"])
            else:
                print(json.dumps(reponse, indent=2))
            
            input("\nAppuie sur Entrée pour continuer...")

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("⚠️  Ce serveur est conçu pour Windows.")
        print("   Les agents peuvent tourner sur Windows.")
    
    server = PegasusServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nArrêt demandé...")
        server.running = False