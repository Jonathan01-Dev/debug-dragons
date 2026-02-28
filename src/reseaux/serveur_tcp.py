import socket
import threading
from reseaux.table_pairs import TablePairs

# Paramètres
DEFAULT_TCP_PORT = 7777
MAX_CONNEXIONS = 10

class ServeurTCP:
    """Serveur TCP pour gérer PEER_LIST et futur transfert de chunks"""
    def __init__(self, table_pairs: TablePairs, port=DEFAULT_TCP_PORT):
        self.table_pairs = table_pairs
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.listen(MAX_CONNEXIONS)
        print(f"[ServeurTCP] Serveur TCP prêt sur le port {self.port}")

    def handle_client(self, client_sock, addr):
        """Gérer un client TCP"""
        print(f"[ServeurTCP] Connexion TCP depuis {addr}")
        try:
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                # Ici on pourrait parser TLV pour messages/chunks
                # Pour l'instant on affiche simplement le message reçu
                print(f"[ServeurTCP] Reçu de {addr}: {data.decode()}")
        except Exception as e:
            print(f"[ServeurTCP] Erreur client {addr}: {e}")
        finally:
            client_sock.close()
            print(f"[ServeurTCP] Connexion fermée: {addr}")

    def start(self):
        """Boucle principale d'écoute TCP"""
        print(f"[ServeurTCP] Serveur TCP lancé et en écoute sur le port {self.port}")
        while True:
            client_sock, addr = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(client_sock, addr), daemon=True).start()