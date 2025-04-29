import socket
import pickle
import threading
import time

class ClientJeu:
    def __init__(self):
        self.client_socket = None
        self.connexion_active = False
        
        # État du jeu
        self.plateaux_places = [None, None, None, None]
        self.joueur_pret = False
        self.adversaire_pret = False
    
    def connecter(self, ip, port, code_salon):
        """Se connecte au serveur de jeu"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.connexion_active = True
            
            # Démarrer le thread d'écoute
            thread_reception = threading.Thread(target=self.recevoir_donnees)
            thread_reception.daemon = True
            thread_reception.start()
            
            print(f"Connecté à l'hôte {ip}:{port} !")
            return True
            
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
    
    def recevoir_donnees(self):
        """Thread qui écoute les données entrantes du serveur"""
        while self.connexion_active:
            try:
                # Recevoir la taille des données
                taille_donnees = self.client_socket.recv(4)
                if not taille_donnees:
                    print("Connexion perdue avec le serveur")
                    self.connexion_active = False
                    break
                
                taille = int.from_bytes(taille_donnees, byteorder='big')
                
                # Recevoir les données
                donnees = b''
                while len(donnees) < taille:
                    chunk = self.client_socket.recv(min(4096, taille - len(donnees)))
                    if not chunk:
                        break
                    donnees += chunk
                
                # Désérialiser les données
                if donnees:
                    message = pickle.loads(donnees)
                    self.traiter_message(message)
                
            except Exception as e:
                print(f"Erreur dans la réception des données: {e}")
                self.connexion_active = False
                break
    
    def traiter_message(self, message):
        """Traite le message reçu du serveur"""
        type_message = message.get("type")
        contenu = message.get("contenu")
        
        if type_message == "plateau":
            # Mettre à jour les plateaux de l'adversaire
            self.plateaux_places = contenu
            print("Plateaux adversaires mis à jour")
        
        elif type_message == "pret":
            # L'adversaire est prêt
            self.adversaire_pret = contenu
            print(f"Adversaire {'prêt' if contenu else 'pas prêt'}")
    
    def envoyer_donnees(self, type_message, contenu):
        """Envoie des données au serveur"""
        if not self.client_socket or not self.connexion_active:
            print("Impossible d'envoyer des données: pas de connexion")
            return False
        
        try:
            message = {
                "type": type_message,
                "contenu": contenu
            }
            
            donnees = pickle.dumps(message)
            taille = len(donnees)
            
            # Envoyer d'abord la taille des données
            self.client_socket.sendall(taille.to_bytes(4, byteorder='big'))
            
            # Envoyer les données
            self.client_socket.sendall(donnees)
            return True
            
        except Exception as e:
            print(f"Erreur dans l'envoi des données: {e}")
            self.connexion_active = False
            return False
    
    def mettre_a_jour_plateaux(self, plateaux):
        """Met à jour l'état local des plateaux et envoie au serveur"""
        self.plateaux_places = plateaux
        return self.envoyer_donnees("plateau", plateaux)
    
    def signaler_pret(self, est_pret):
        """Signale que le joueur est prêt"""
        self.joueur_pret = est_pret
        return self.envoyer_donnees("pret", est_pret)
    
    def fermer(self):
        """Ferme la connexion"""
        self.connexion_active = False
        if self.client_socket:
            self.client_socket.close()

if __name__ == "__main__":
    client = ClientJeu()
    try:
        ip_du_serveur = input("IP de l'hôte : ") 
        port_du_serveur = int(input("Port de l'hôte (par défaut 5000) : ") or 5000)
        code_salon = input("Code salon : ")
        
        if client.connecter(ip_du_serveur, port_du_serveur, code_salon):
            # Boucle principale pour tester
            while client.connexion_active:
                time.sleep(1)
    except KeyboardInterrupt:
        print("Client arrêté par l'utilisateur")
    finally:
        client.fermer()