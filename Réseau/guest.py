# ami.py
import socket

ip_du_serveur = input("IP de l'hôte : ") 
port_du_serveur = int(input("Port de l'hôte (par défaut 5000) : ") or 5000)
code_salon = input("Code salon : ")  # À valider côté serveur si tu veux

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip_du_serveur, port_du_serveur))

print("Connecté à l'hôte !")
