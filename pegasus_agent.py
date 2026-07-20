# pegasus_agent.py
#!/usr/bin/env python3
"""PEGASUS - Agent (à exécuter sur les machines à contrôler)"""

import socket
import json
import time
import platform
import subprocess
import sys

# Importe les fonctions communes
from pegasus_common import execute_action, log_event

class PegasusAgent:
    def __init__(self, server_ip="127.0.0.1", port=5000):
        self.server_ip = server_ip
        self.port = port
        self.socket = None
        self.nom = platform.node()  # Nom de la machine
        
    def connect(self):
        """Tente de se connecter au serveur"""
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_ip, self.port))
                print(f"✅ Connecté au serveur {self.server_ip}:{self.port}")
                return True
            except ConnectionRefusedError:
                print(f"⏳ Serveur indisponible ({self.server_ip}:{self.port}), nouvelle tentative dans 5s...")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Erreur de connexion: {e}")
                time.sleep(5)
    
    def identify(self):
        """S'identifie auprès du serveur"""
        try:
            self.socket.send(json.dumps({
                "type": "identify",
                "nom": self.nom,
                "os": platform.system(),
                "version": platform.version()
            }).encode())
        except Exception as e:
            print(f"❌ Erreur d'identification: {e}")
    
    def handle_commands(self):
        """Boucle principale : écoute les commandes du serveur"""
        while True:
            try:
                data = self.socket.recv(4096).decode()
                if not data:
                    print("⚠️ Connexion perdue avec le serveur")
                    break
                
                commande = json.loads(data)
                
                # Si le serveur demande une identification
                if commande.get("type") == "identify":
                    self.identify()
                    continue
                
                # Exécute la commande
                action = commande.get("action")
                params = commande.get("params")
                
                print(f"📩 Reçu: {action} {params if params else ''}")
                resultat = execute_action(action, params)
                
                # Envoie le résultat au serveur
                self.socket.send(json.dumps(resultat).encode())
                
            except json.JSONDecodeError:
                print("❌ Erreur: message mal formé")
            except ConnectionResetError:
                print("⚠️ Connexion réinitialisée par le serveur")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                break
        
        # Reconnexion en cas de perte de connexion
        print("🔄 Tentative de reconnexion...")
        self.socket.close()
        self.reconnect()
    
    def reconnect(self):
        """Tente de se reconnecter en boucle"""
        while True:
            if self.connect():
                self.handle_commands()
            time.sleep(5)
    
    def run(self):
        """Démarre l'agent"""
        print("=" * 60)
        print("🐴 PEGASUS AGENT")
        print(f"   Machine: {self.nom}")
        print(f"   Serveur: {self.server_ip}:{self.port}")
        print("=" * 60)
        
        log_event(f"Agent démarré sur {self.nom}")
        
        if self.connect():
            self.handle_commands()

if __name__ == "__main__":
    # Paramètres de connexion
    if len(sys.argv) > 1:
        SERVER_IP = sys.argv[1]  # Peut être passé en argument
    else:
        SERVER_IP = input("IP du serveur (défaut: 127.0.0.1): ").strip() or "127.0.0.1"
    
    agent = PegasusAgent(server_ip=SERVER_IP)
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n🛑 Agent arrêté.")
        log_event("Agent arrêté")