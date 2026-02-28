Protocole P2P Chiffré et Décentralisé à Zéro-Connexion

1.	Stack technique choisie

Langage principal :
Notre groupe a retenu le langage python à cause des raisons suivantes : 
•	Rapidité de prototypage 
•	Support natif solide pour la programmation réseau (socket, asyncio)
•	Disponibilité de bibliothèques cryptographiques fiables (PyNaCl)
•	Lisibilité du code facilitant les debugs

Technologie de transport :
Le protocole retenu pour le transport rapide de fichiers sans connexion est UDP : User Datagram Protocol.  
Ce choix permet :
•	une découverte automatique rapide sur LAN
•	une communication simple sans dépendance à une infrastructure lourde
•	une implémentation rapide et robuste dans le temps limité du hackathon

PKI — Identité des nœuds :
Chaque nœud génère localement une paire de clés :
•	Ed25519 pour l’identité et la signature
•	clé publique = Node ID
•	clé privée = signature locale


2.	Structure binaire minimale implémentée :
┌─────────────────────────────────────────────────────────┐
│  MAGIC (4 bytes)                                        │
│  TYPE (1 byte)                                          │
│  NODE_ID (32 bytes)                                     │
│  PAYLOAD_LEN (4 bytes, uint32 BE)                       │
├─────────────────────────────────────────────────────────┤
│  PAYLOAD (longueur variable, chiffré)                   │
├─────────────────────────────────────────────────────────┤
│  HMAC-SHA256 (32 bytes)                                 │
└─────────────────────────────────────────────────────────┘


Types de paquets :
Code	Type	          Description
0x01	HELLO	          Annonce de présence
0x02	PEER_LIST	      liste des pairs
0x03	MSG	              Message chiffré
0x04	CHUNK_REQ	      Requête de chunk
0x05	CHUNK_DATA        Données chunk
0x06	MANIFEST	      Métadonnées fichier
0x07	ACK	              Acquittement


3.	Schéma d’architecture
 
    ___________________________________________________________
      |                                                     |
      |             UDP Multicast Discovery                 |
      |           (Addr: 239.255.42.99:6000)                |
      |_____________________________________________________|
                 |               |               |
                 v               v               v
          +------------+   +------------+   +------------+
          |   Node A   |<->|   Node B   |<->|   Node C   |
          +------------+   +------------+   +------------+
          | TCP : 7777 |   | TCP : 7778 |   | TCP : 7779 |
          +------------+   +------------+   +------------+
                 ^               ^               ^
                 |_______________|_______________|
                         Communication TCP
                    (Handshake Noise Protocol)

Composants :
•	Découverte et communication : UDP Multicast
•	Identité : Ed25519
•	Intégrité paquet : HMAC-SHA256
•	Chiffrement E2E : prévu au Sprint 2