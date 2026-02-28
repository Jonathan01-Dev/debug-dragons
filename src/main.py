import threading
import time
from reseaux.table_pairs import TablePairs
from reseaux.decouverte_udp import DecouverteUDP
from reseaux.serveur_tcp import ServeurTCP

def lancer_noeud(node_id, tcp_port):
    """
    Fonction pour lancer un nœud complet :
    - Serveur TCP
    - Découverte UDP
    - Affichage des pairs actifs toutes les 5 secondes
    """
    # 1️⃣ Création de la table de pairs
    peer_table = TablePairs()
    peer_table.charger()  # On charge la table existante si dispo

    # 2️⃣ Serveur TCP
    tcp_server = ServeurTCP(table_pairs=peer_table, port=tcp_port)
    threading.Thread(target=tcp_server.start, daemon=True).start()
    print(f"[{node_id}] Serveur TCP lancé sur le port {tcp_server.port}")

    # 3️⃣ Découverte UDP
    udp_discovery = DecouverteUDP(node_id=node_id, tcp_port=tcp_port, table_pairs=peer_table)
    udp_discovery.demarrer()
    print(f"[{node_id}] Découverte UDP lancée")

    # 4️⃣ Boucle principale : affichage pairs actifs et nettoyage
    try:
        while True:
            peer_table.cleanup(timeout=90)      # Supprime pairs inactifs
            peers = peer_table.get_all()        # Récupère copie table
            print(f"[{node_id}] Pairs actifs ({len(peers)}):")
            for nid, info in peers.items():
                last_seen = int(time.time() - info["last_seen"])
                print(f"    {nid} -> {info['ip']}:{info['tcp_port']} (last_seen={last_seen}s)")
            peer_table.sauvegarder()            # Sauvegarde si changements
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"[{node_id}] Arrêt du nœud")

if __name__ == "__main__":
    # 🔹 Configuration des nœuds à tester
    noeuds = [
        {"node_id": "node_001", "tcp_port": 7777},
        {"node_id": "node_002", "tcp_port": 7778},
        {"node_id": "node_003", "tcp_port": 7779},
    ]

    # 🔹 Lancer chaque nœud dans un thread séparé
    threads = []
    for n in noeuds:
        t = threading.Thread(target=lancer_noeud, args=(n["node_id"], n["tcp_port"]), daemon=True)
        t.start()
        threads.append(t)

    # 🔹 Boucle pour garder le main actif
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[MAIN] Arrêt de tous les nœuds")