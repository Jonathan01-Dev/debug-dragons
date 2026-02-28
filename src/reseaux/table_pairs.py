import threading
import time
import json

class TablePairs:
    """
    Classe thread-safe pour gérer les pairs connus
    - Supprime les pairs inactifs (timeout)
    - Persistance JSON pour reload après redémarrage
    """
    def __init__(self, filename="peers.json"):
        self.lock = threading.Lock()
        self.pairs = {}  # node_id -> info
        self.filename = filename
        self.changes = False  # Flag pour savoir si sauvegarder

    def ajouter_ou_mettre_a_jour(self, node_id, ip, tcp_port, shared_files=None, reputation=1.0):
        """Ajoute ou met à jour un pair"""
        with self.lock:
            last_seen_prev = self.pairs.get(node_id, {}).get("last_seen", 0)
            now = time.time()
            # On ne met à jour que si last_seen a changé pour éviter spam logs
            if now - last_seen_prev >= 1:
                self.pairs[node_id] = {
                    "ip": ip,
                    "tcp_port": tcp_port,
                    "last_seen": now,
                    "shared_files": shared_files or [],
                    "reputation": reputation
                }
                self.changes = True
                print(f"[TablePairs] Pair ajouté/mis à jour: {node_id} ({ip}:{tcp_port})")

    def supprimer(self, node_id):
        """Supprime un pair"""
        with self.lock:
            if node_id in self.pairs:
                del self.pairs[node_id]
                self.changes = True

    def cleanup(self, timeout=90):
        """Supprime les pairs qui n'ont pas envoyé de HELLO depuis timeout secondes"""
        now = time.time()
        to_delete = []
        with self.lock:
            for node_id, info in self.pairs.items():
                if now - info["last_seen"] > timeout:
                    to_delete.append(node_id)
            for node_id in to_delete:
                del self.pairs[node_id]
                self.changes = True
                print(f"[TablePairs] Pair supprimé pour timeout: {node_id}")

    def get_all(self):
        """Retourne une copie thread-safe des pairs"""
        with self.lock:
            return self.pairs.copy()

    def sauvegarder(self):
        """Sauvegarde la table sur disque si modifiée"""
        if self.changes:
            with self.lock:
                with open(self.filename, "w") as f:
                    json.dump(self.pairs, f, indent=2)
                self.changes = False
                print("[TablePairs] Table sauvegardée sur disque")

    def charger(self):
        """Charge la table depuis un fichier JSON"""
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
            with self.lock:
                self.pairs = data
                print("[TablePairs] Table chargée depuis le disque")
        except FileNotFoundError:
            self.pairs = {}