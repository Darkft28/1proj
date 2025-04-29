import socket
import random
import pickle
import threading
import time

class ServeurJeu:
    def __init__(self):
        self.code_salon = self.generer_code_salon()
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.PORT = 5000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()
        
        # État du jeu
        self.plateaux_places = [None, None, None, None]
        self.joueur_pret = False
        self.adversaire_pret = False
        self.connexion_active = True
        
        # Connexion client
        self.conn = None
        self.addr = None

    def generer_code_salon(self):
        # Génère un code aléatoire à 4 chiffres
        return random.randint(1000, 9999)
    
    def accepter_connexion(self):
        print(f"Adresse IP : {self.HOST}, Port : {self.PORT}, Code salon : {self.code_salon}")
        print("En attente de connexion...")
        self.conn, self.addr = self.server_socket.accept()
        print(f"Joueur connecté depuis {self.addr}")
        
        # Démarrer le thread d'écoute
        thread_reception = threading.Thread(target=self.recevoir_donnees)
        thread_reception.daemon = True
        thread_reception.start()
        return True
    
    def recevoir_donnees(self):
        """Thread qui écoute les données entrantes du client"""
        while self.connexion_active:
            try:
                # Recevoir la taille des données
                taille_donnees = self.conn.recv(4)
                if not taille_donnees:
                    print("Connexion perdue avec le client")
                    self.connexion_active = False
                    break
                
                taille = int.from_bytes(taille_donnees, byteorder='big')
                
                # Recevoir les données
                donnees = b''
                while len(donnees) < taille:
                    chunk = self.conn.recv(min(4096, taille - len(donnees)))
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
        """Traite le message reçu du client"""
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
        """Envoie des données au client"""
        if not self.conn or not self.connexion_active:
            print("Impossible d'envoyer des données: pas de connexion client")
            return False
        
        try:
            message = {
                "type": type_message,
                "contenu": contenu
            }
            
            donnees = pickle.dumps(message)
            taille = len(donnees)
            
            # Envoyer d'abord la taille des données
            self.conn.sendall(taille.to_bytes(4, byteorder='big'))
            
            # Envoyer les données
            self.conn.sendall(donnees)
            return True
            
        except Exception as e:
            print(f"Erreur dans l'envoi des données: {e}")
            self.connexion_active = False
            return False
    
    def mettre_a_jour_plateaux(self, plateaux):
        """Met à jour l'état local des plateaux et envoie au client"""
        self.plateaux_places = plateaux
        return self.envoyer_donnees("plateau", plateaux)
    
    def signaler_pret(self, est_pret):
        """Signale que le joueur est prêt"""
        self.joueur_pret = est_pret
        return self.envoyer_donnees("pret", est_pret)
    
    def fermer(self):
        """Ferme la connexion et le serveur"""
        self.connexion_active = False
        if self.conn:
            self.conn.close()
        self.server_socket.close()

if __name__ == "__main__":
    serveur = ServeurJeu()
    try:
        serveur.accepter_connexion()
        # Boucle principale pour tester
        while serveur.connexion_active:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Serveur arrêté par l'utilisateur")
    finally:
        serveur.fermer()