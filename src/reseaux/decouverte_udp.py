import socket
import struct
import threading
import time
import json
from reseaux.table_pairs import TablePairs

# Paramètres configurables
MULTICAST_GROUP = '239.255.42.99'
MULTICAST_PORT = 6000
HELLO_INTERVAL = 30  # secondes

class DecouverteUDP:
    """Découverte de pairs via UDP multicast"""
    def __init__(self, node_id, tcp_port, table_pairs: TablePairs):
        self.node_id = node_id
        self.tcp_port = tcp_port
        self.table_pairs = table_pairs

        # Création du socket UDP multicast
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MULTICAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def build_hello_packet(self):
        """Crée le paquet HELLO au format JSON"""
        pkt = {
            "type": "HELLO",
            "node_id": self.node_id,
            "tcp_port": self.tcp_port,
            "timestamp": time.time()
        }
        return json.dumps(pkt).encode('utf-8')

    def envoyer_hello(self):
        """Envoie HELLO toutes les 30s"""
        while True:
            packet = self.build_hello_packet()
            self.sock.sendto(packet, (MULTICAST_GROUP, MULTICAST_PORT))
            print(f"[UDP] HELLO envoyé depuis {self.node_id}")
            time.sleep(HELLO_INTERVAL)

    def recevoir_paquets(self):
        """Réception des paquets UDP et mise à jour TablePairs"""
        while True:
            data, addr = self.sock.recvfrom(1024)
            try:
                pkt = json.loads(data.decode('utf-8'))
                if pkt["type"] == "HELLO" and pkt["node_id"] != self.node_id:
                    self.table_pairs.ajouter_ou_mettre_a_jour(
                        pkt["node_id"], addr[0], pkt["tcp_port"]
                    )
            except Exception as e:
                print("[UDP] Erreur réception:", e)

    def demarrer(self):
        """Démarre l’envoi et la réception en threads séparés"""
        threading.Thread(target=self.envoyer_hello, daemon=True).start()
        threading.Thread(target=self.recevoir_paquets, daemon=True).start()
        print("[UDP] Découverte UDP démarrée")