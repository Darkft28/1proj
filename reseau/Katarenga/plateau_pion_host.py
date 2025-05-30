import pygame
import sys
import json
import socket
import threading
import random
import string
from menu.config import get_theme
import os

# Répertoire du fichier en cours
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Plateau_pion_host:
    def __init__(self):
        pygame.init()
        
        self.font_path = pygame.font.match_font('assets/police-gloomie_saturday/Gloomie Saturday.otf')
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h

        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440

        # Initialisation de la fenêtre de jeu
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Katarenga - HOST")
        
        # Import pyperclip pour la copie dans le presse-papier
        try:
            import pyperclip
            self.pyperclip = pyperclip
        except ImportError:
            print("pyperclip non installé - Les boutons copier ne fonctionneront pas")
            print("Installez avec: pip install pyperclip")
            self.pyperclip = None
        
        # Taille des cases
        self.TAILLE_CASE = int(100 * self.RATIO_X)
        self.OFFSET_X = (self.LARGEUR - 10 * self.TAILLE_CASE) // 2
        self.OFFSET_Y = (self.HAUTEUR - 10 * self.TAILLE_CASE) // 2
        
        # Fond d'écran
        theme = get_theme()
        if theme == "Sombre":
            self.background_image = pygame.image.load("assets/menu/menu-sombre.png")
        else:
            self.background_image = pygame.image.load("assets/menu/menu-claire.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))

        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        self.GRIS = (128, 128, 128)

        self.images = {}
        try:
            image_paths = {
                self.ROUGE: "assets/image_rouge.png",
                self.BLEU: "assets/image_bleue.png",
                self.JAUNE: "assets/image_jaune.png",
                self.VERT: "assets/image_verte.png"
            }
            for couleur, path in image_paths.items():
                self.images[couleur] = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Erreur lors du chargement des images: {e}")

        # Bords et coins
        self.BORDURE = "assets/bordure.png"
        self.COINS = "assets/coin.png"

        # Pions
        try:
            self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
            self.pion_noir = pygame.image.load("assets/pion_noir.png")
        except:
            self.pion_blanc = None
            self.pion_noir = None

        # Plateau de pions initial (10x10 avec bordures)
        self.plateau = [[3, 10, 10, 10, 10, 10, 10, 10, 10, 3],
                        [10, 2, 2, 2, 2, 2, 2, 2, 2, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 1, 1, 1, 1, 1, 1, 1, 1, 10],
                        [4, 10, 10, 10, 10, 10, 10, 10, 10, 4]]
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # État du jeu
        self.game_over = False
        self.gagnant = None
        self.joueur_actuel = 1
        self.mon_numero = 1  # Host est toujours joueur 1
        
        # Variables de jeu
        self.pion_selectionne = None
        self.mouvements_possibles = []
        
        # Réseau
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.connecte = False
        self.ip_locale = self.obtenir_ip_locale()
        self.port = 12345
        
        # Interface
        self.etat_interface = "attente_connexion"  # "attente_connexion", "jeu"
        self.bouton_abandonner = None
        self.bouton_rejouer = None
        self.bouton_quitter = None

    def transformer_plateau(self):
        """Génère le plateau Katarenga 10x10 à partir du plateau_finale.json"""
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
                plateau_8 = json.load(f)
                
                # Si le plateau est déjà 10x10, on l'utilise tel quel
                if len(plateau_8) == 10 and len(plateau_8[0]) == 10:
                    return
                
                # Sinon, on transforme le plateau 8x8 en 10x10
                plateau_8.insert(0, [self.BORDURE for _ in range(8)])
                plateau_8.append([self.BORDURE for _ in range(8)])

                for row in plateau_8:
                    row.insert(0, self.BORDURE)
                    row.append(self.BORDURE)

                # Coins
                plateau_8[0][0] = self.COINS
                plateau_8[0][9] = self.COINS
                plateau_8[9][0] = self.COINS
                plateau_8[9][9] = self.COINS
                
                with open("plateaux/plateau_katarenga.json", 'w') as fw:
                    json.dump(plateau_8, fw, indent=2)
                fw.close()
            f.close()

        except Exception as e:
            print(f"Erreur lors du chargement du plateau: {e}")

    def obtenir_ip_locale(self):
        """Obtient l'adresse IP locale"""
        try:
            # Connexion temporaire pour obtenir l'IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def demarrer_serveur(self):
        """Démarre le serveur en mode host"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip_locale, self.port))
            self.server_socket.listen(1)
            print(f"Serveur démarré sur {self.ip_locale}:{self.port}")
            
            # Attendre une connexion
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"Client connecté depuis {self.client_address}")
            self.connecte = True
            self.etat_interface = "jeu"
            
            # Démarrer le thread de réception
            thread_reception = threading.Thread(target=self.ecouter_messages)
            thread_reception.daemon = True
            thread_reception.start()
            
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur: {e}")

    def ecouter_messages(self):
        """Écoute les messages du client"""
        try:
            while self.connecte:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.traiter_message(message)
                else:
                    break
        except:
            self.connecte = False
            print("Connexion fermée par le client")

    def traiter_message(self, message):
        """Traite les messages reçus du client"""
        if message.startswith("MOVE:"):
            # Format: MOVE:ligne_dep,col_dep,ligne_arr,col_arr
            coords = message[5:].split(',')
            if len(coords) == 4:
                ligne_dep, col_dep, ligne_arr, col_arr = map(int, coords)
                self.deplacer_pion((ligne_dep, col_dep), (ligne_arr, col_arr))
                self.joueur_actuel = self.mon_numero
                
                if self.verifier_victoire(2):
                    self.game_over = True
                    self.gagnant = "Joueur 2"
                    
        elif message == "GAME_OVER":
            self.game_over = True

    def envoyer_message(self, message):
        """Envoie un message au client"""
        if self.connecte and self.client_socket:
            try:
                self.client_socket.send(message.encode())
            except:
                self.connecte = False

    def dessiner_plateau(self):
        """Dessine le plateau de jeu avec les images"""
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
                plateau_images = json.load(f)
            
            # Dessiner les images du plateau
            for i in range(10):
                for j in range(10):
                    image_path = plateau_images[i][j]
                    
                    # Charger l'image si elle n'est pas déjà en cache
                    if image_path not in self.images:
                        try:
                            self.images[image_path] = pygame.image.load(image_path).convert_alpha()
                            self.images[image_path] = pygame.transform.scale(self.images[image_path], 
                                                                        (self.TAILLE_CASE, self.TAILLE_CASE))
                        except pygame.error as e:
                            print(f"Erreur lors du chargement de l'image {image_path}: {e}")
                            continue
                    
                    # Dessiner l'image
                    self.ecran.blit(self.images[image_path], 
                                (self.OFFSET_X + j * self.TAILLE_CASE, 
                                self.OFFSET_Y + i * self.TAILLE_CASE))

        except Exception as e:
            print(f"Erreur lors du chargement du plateau: {e}")
            # Fallback: dessiner un damier basique
            for i in range(10):
                for j in range(10):
                    couleur = self.BLANC if (i + j) % 2 == 0 else self.GRIS
                    pygame.draw.rect(self.ecran, couleur, 
                                   (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))

    def afficher_plateau(self):
        """Affiche les pions sur le plateau"""
        pion_size = int(self.TAILLE_CASE * 0.8)
        offset = (self.TAILLE_CASE - pion_size) // 2
        
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == 1:  # Pion blanc (host)
                    if self.pion_blanc:
                        pion_scaled = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
                        self.ecran.blit(pion_scaled, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE + offset, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                    else:
                        pygame.draw.circle(self.ecran, self.BLANC,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2)
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2, 2)
                elif self.plateau[i][j] == 2:  # Pion noir (client)
                    if self.pion_noir:
                        pion_scaled = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
                        self.ecran.blit(pion_scaled, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE + offset, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                    else:
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2)

    def afficher_pion_selectionne(self):
        """Affiche une bordure autour du pion sélectionné"""
        if self.pion_selectionne:
            ligne, col = self.pion_selectionne
            pygame.draw.rect(self.ecran, self.ROUGE, 
                           (self.OFFSET_X + col * self.TAILLE_CASE, 
                            self.OFFSET_Y + ligne * self.TAILLE_CASE, 
                            self.TAILLE_CASE, self.TAILLE_CASE), 4)

    def afficher_mouvements_possibles(self):
        """Affiche des cercles pour les mouvements possibles"""
        if self.pion_selectionne and self.mouvements_possibles:
            rayon = self.TAILLE_CASE // 4
            for ligne, col in self.mouvements_possibles:
                centre_x = self.OFFSET_X + col * self.TAILLE_CASE + self.TAILLE_CASE // 2
                centre_y = self.OFFSET_Y + ligne * self.TAILLE_CASE + self.TAILLE_CASE // 2
                pygame.draw.circle(self.ecran, self.VERT, (centre_x, centre_y), rayon)

    def mouvement_valide(self, depart, arrivee):
        """Vérifie si un mouvement est valide selon les règles de Katarenga"""
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        # Vérifier que la destination n'est pas occupée par un pion allié
        if self.plateau[ligne_arr][col_arr] == self.joueur_actuel:
            return False
        
        # Vérifier que la destination n'est pas une bordure
        if self.plateau[ligne_arr][col_arr] == 10:
            return False
        
        # Cas spécial : pion sur la ligne adverse
        if (self.joueur_actuel == 1 and ligne_dep == 1) or \
           (self.joueur_actuel == 2 and ligne_dep == 8):
            # Si le pion est sur la ligne adverse, il peut aller dans un camp adverse
            if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3) or \
               (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4):
                return True
        
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
                plateau_images = json.load(f)
            
            if ligne_dep >= len(plateau_images) or col_dep >= len(plateau_images[0]):
                return False
                
            image_path = plateau_images[ligne_dep][col_dep]
            
            if "rouge" in image_path.lower():
                # Mouvement en ligne droite
                return (ligne_arr == ligne_dep or col_arr == col_dep) and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "bleu" in image_path.lower():
                # Mouvement de roi
                return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1 and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "jaune" in image_path.lower():
                # Mouvement en diagonale
                return abs(ligne_arr - ligne_dep) == abs(col_arr - col_dep) and ligne_arr != ligne_dep
            elif "vert" in image_path.lower():
                # Mouvement de cavalier
                return (abs(ligne_arr - ligne_dep) == 2 and abs(col_arr - col_dep) == 1) or \
                       (abs(ligne_arr - ligne_dep) == 1 and abs(col_arr - col_dep) == 2)
            else:
                return True
                
        except Exception as e:
            print(f"Erreur lors de la vérification des règles: {e}")
            return False

    def get_mouvements_possibles(self, ligne, col):
        """Retourne tous les mouvements possibles pour un pion donné"""
        mouvements = []
        for i in range(10):
            for j in range(10):
                if self.mouvement_valide((ligne, col), (i, j)):
                    mouvements.append((i, j))
        return mouvements

    def deplacer_pion(self, depart, arrivee):
        """Déplace un pion d'une position à une autre"""
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        # Vérifier si le pion va dans un camp adverse
        pion_entre_dans_camp = False
        if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3) or \
           (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4):
            pion_entre_dans_camp = True
        
        # Capturer le pion ennemi s'il y en a un
        if self.plateau[ligne_arr][col_arr] in [1, 2] and not pion_entre_dans_camp:
            pion_capture = self.plateau[ligne_arr][col_arr]
        
        # Déplacer le pion
        if pion_entre_dans_camp:
            self.plateau[ligne_dep][col_dep] = 0
        else:
            self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
            self.plateau[ligne_dep][col_dep] = 0

    def verifier_victoire(self, joueur):
        """Vérifie si un joueur a gagné"""
        # Compter les pions du joueur adverse
        pions_adversaire = 0
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == (3 - joueur):
                    pions_adversaire += 1
        
        return pions_adversaire == 0

    def afficher_interface_attente(self):
        """Affiche l'interface d'attente de connexion"""
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        
        # Titre
        texte_titre = police.render("En attente d'un adversaire...", True, self.BLANC)
        rect_titre = texte_titre.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 200))
        self.ecran.blit(texte_titre, rect_titre)
        
        # Informations de connexion
        police_info = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 30)
        
        info_ip = f"Votre IP: {self.ip_locale}"
        info_port = f"Port: {self.port}"
        
        texte_ip = police_info.render(info_ip, True, self.BLANC)
        texte_port = police_info.render(info_port, True, self.BLANC)
        
        rect_ip = texte_ip.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 100))
        rect_port = texte_port.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 50))
        
        self.ecran.blit(texte_ip, rect_ip)
        self.ecran.blit(texte_port, rect_port)
        
        # Boutons de copie
        if self.pyperclip:
            largeur_bouton = 200
            hauteur_bouton = 50
            
            bouton_copier_ip = pygame.Rect(
                self.LARGEUR // 2 - largeur_bouton - 10,
                self.HAUTEUR // 2 + 50,
                largeur_bouton,
                hauteur_bouton
            )
            
            bouton_copier_tout = pygame.Rect(
                self.LARGEUR // 2 + 10,
                self.HAUTEUR // 2 + 50,
                largeur_bouton,
                hauteur_bouton
            )
            
            pygame.draw.rect(self.ecran, self.BLEU, bouton_copier_ip, border_radius=20)
            pygame.draw.rect(self.ecran, self.VERT, bouton_copier_tout, border_radius=20)
            
            police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 25)
            
            texte_copier_ip = police_bouton.render("Copier IP", True, self.BLANC)
            texte_copier_tout = police_bouton.render("Copier Tout", True, self.BLANC)
            
            rect_texte_ip = texte_copier_ip.get_rect(center=bouton_copier_ip.center)
            rect_texte_tout = texte_copier_tout.get_rect(center=bouton_copier_tout.center)
            
            self.ecran.blit(texte_copier_ip, rect_texte_ip)
            self.ecran.blit(texte_copier_tout, rect_texte_tout)
            
            # Stocker les boutons pour la gestion des clics
            self.bouton_copier_ip = bouton_copier_ip
            self.bouton_copier_tout = bouton_copier_tout

    def afficher_tour(self):
        """Affiche le tour actuel"""
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 35)
        
        if self.joueur_actuel == self.mon_numero:
            texte = "Votre tour"
            couleur = self.VERT
        else:
            texte = "Tour de l'adversaire"
            couleur = self.ROUGE
        
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))

    def afficher_info_jeu(self):
        """Affiche les informations du jeu"""
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 25)
        
        # Compter les pions
        pions_joueur = 0
        pions_adversaire = 0
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == 1:
                    pions_joueur += 1
                elif self.plateau[i][j] == 2:
                    pions_adversaire += 1
        
        texte = f"Vos pions: {pions_joueur} | Pions adversaire: {pions_adversaire}"
        surface_texte = police.render(texte, True, self.NOIR)
        self.ecran.blit(surface_texte, (20, self.HAUTEUR - 60))

        # Bouton abandonner
        if not self.game_over and self.joueur_actuel == self.mon_numero:
            largeur_bouton = 220
            hauteur_bouton = 50
            self.bouton_abandonner = pygame.Rect(
                self.LARGEUR - largeur_bouton - 30,
                self.HAUTEUR - hauteur_bouton - 30,
                largeur_bouton,
                hauteur_bouton
            )
            pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_abandonner, border_radius=20)
            texte_abandonner = police.render("Abandonner", True, self.BLANC)
            rect_texte_abandonner = texte_abandonner.get_rect(center=self.bouton_abandonner.center)
            self.ecran.blit(texte_abandonner, rect_texte_abandonner)
        else:
            self.bouton_abandonner = None

    def gerer_clic(self):
        """Gère les clics de souris"""
        if self.joueur_actuel != self.mon_numero:
            return
            
        pos = pygame.mouse.get_pos()
        
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        if 0 <= ligne < 10 and 0 <= col < 10:
            if self.pion_selectionne is None:
                # Sélection d'un pion
                if self.plateau[ligne][col] == self.joueur_actuel:
                    self.pion_selectionne = (ligne, col)
                    self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
            else:
                # Déplacement d'un pion
                if self.mouvement_valide(self.pion_selectionne, (ligne, col)):
                    # Envoyer le mouvement au client
                    ligne_dep, col_dep = self.pion_selectionne
                    message = f"MOVE:{ligne_dep},{col_dep},{ligne},{col}"
                    self.envoyer_message(message)
                    
                    self.deplacer_pion(self.pion_selectionne, (ligne, col))
                    self.pion_selectionne = None
                    self.mouvements_possibles = []
                    
                    # Vérifier victoire
                    if self.verifier_victoire(self.mon_numero):
                        self.game_over = True
                        self.gagnant = "Vous"
                        self.envoyer_message("GAME_OVER")
                    else:
                        self.joueur_actuel = 2  # Passer le tour à l'adversaire
                else:
                    # Annuler la sélection
                    self.pion_selectionne = None
                    self.mouvements_possibles = []

    def run(self):
        """Boucle principale du jeu"""
        # Initialiser le plateau
        self.transformer_plateau()
        
        # Démarrer le serveur en thread séparé
        thread_serveur = threading.Thread(target=self.demarrer_serveur)
        thread_serveur.daemon = True
        thread_serveur.start()
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    if self.etat_interface == "attente_connexion":
                        # Gestion des clics sur les boutons de copie
                        if hasattr(self, 'bouton_copier_ip') and self.bouton_copier_ip.collidepoint(x, y):
                            if self.pyperclip:
                                self.pyperclip.copy(self.ip_locale)
                                print("IP copiée dans le presse-papier")
                        elif hasattr(self, 'bouton_copier_tout') and self.bouton_copier_tout.collidepoint(x, y):
                            if self.pyperclip:
                                self.pyperclip.copy(f"{self.ip_locale}:{self.port}")
                                print("IP:Port copiés dans le presse-papier")
                    
                    elif self.etat_interface == "jeu":
                        if not self.game_over:
                            if self.bouton_abandonner and self.bouton_abandonner.collidepoint(x, y):
                                self.game_over = True
                                self.gagnant = "Adversaire"
                                self.envoyer_message("GAME_OVER")
                            else:
                                self.gerer_clic()
            
            # Affichage
            self.ecran.blit(self.background_image, (0, 0))
            
            if self.etat_interface == "attente_connexion":
                self.afficher_interface_attente()
            elif self.etat_interface == "jeu":
                self.dessiner_plateau()
                self.afficher_plateau()
                self.afficher_pion_selectionne()
                self.afficher_mouvements_possibles()
                
                if not self.game_over:
                    self.afficher_tour()
                    self.afficher_info_jeu()
                else:
                    # Afficher fin de jeu
                    police_grand = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
                    texte_fin = f"{self.gagnant} gagne!"
                    surface_fin = police_grand.render(texte_fin, True, self.BLANC)
                    rect_fin = surface_fin.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2))
                    self.ecran.blit(surface_fin, rect_fin)
            
            pygame.display.flip()
            clock.tick(60)
        
        # Nettoyage
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        
        pygame.quit()


if __name__ == "__main__":
    host = Plateau_pion_host()
    host.run()
