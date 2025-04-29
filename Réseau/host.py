import socket
import random

def generer_code_salon():
    # Génère un code aléatoire à 4 chiffres
    return random.randint(1000, 9999)

code_salon = generer_code_salon()
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


print(f"Adresse IP : {HOST}, Port : {PORT}, Code salon : {code_salon}")

print("En attente de connexion...")
conn, addr = server_socket.accept()
print(f"Joueur connecté depuis {addr}")
