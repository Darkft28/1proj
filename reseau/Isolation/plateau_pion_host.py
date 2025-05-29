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
        pygame.display.set_caption("Isolation - HOST")
        
        # Import pyperclip pour la copie dans le presse-papier
        try:
            import pyperclip
            self.pyperclip = pyperclip
        except ImportError:
            print("pyperclip non installé - Les boutons copier ne fonctionneront pas")
            print("Installez avec: pip install pyperclip")
            self.pyperclip = None
        
        # Taille des cases
        self.TAILLE_CASE = int(120 * self.RATIO_X)
        self.OFFSET_X = (self.LARGEUR - 8 * self.TAILLE_CASE) // 2
        self.OFFSET_Y = (self.HAUTEUR - 8 * self.TAILLE_CASE) // 2
        
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
        self.ROUGE_CLAIR = (255, 100, 100)

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

        # Pions
        try:
            self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
            self.pion_noir = pygame.image.load("assets/pion_noir.png")
        except:
            self.pion_blanc = None
            self.pion_noir = None

        # Plateau de base
        self.plateau = [[0 for _ in range(8)] for _ in range(8)]
        self.cases_bloquees = [[False for _ in range(8)] for _ in range(8)]
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # État du jeu
        self.game_over = False
        self.gagnant = None
        self.joueur_actuel = 1
        self.mon_numero = 1  # Host est toujours joueur 1
        
        # Réseau
        self.client_socket = None
        self.server_socket = None
        self.connexion_etablie = False
        self.code_salon = self.generer_code_salon()
        self.ip_locale = self.obtenir_ip_locale()
        self.port = 5555
        
        # État de l'écran
        self.ecran_attente = True
        
        # Initialiser le serveur
        self.initialiser_serveur()

    def generer_code_salon(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def obtenir_ip_locale(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def initialiser_serveur(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip_locale, self.port))
        self.server_socket.listen(1)
        
        # Thread pour accepter les connexions
        thread_accepter = threading.Thread(target=self.accepter_connexion)
        thread_accepter.daemon = True
        thread_accepter.start()
    
    def accepter_connexion(self):
        print(f"Serveur en attente sur {self.ip_locale}:{self.port}")
        self.client_socket, adresse = self.server_socket.accept()
        print(f"Connexion acceptée de {adresse}")
        
        # Envoyer le code de salon pour vérification
        self.client_socket.send(self.code_salon.encode())
        
        # Recevoir la confirmation
        confirmation = self.client_socket.recv(1024).decode()
        if confirmation == "OK":
            self.connexion_etablie = True
            self.ecran_attente = False
            
            # Thread pour recevoir les messages
            thread_recevoir = threading.Thread(target=self.recevoir_messages)
            thread_recevoir.daemon = True
            thread_recevoir.start()
    
    def recevoir_messages(self):
        while self.connexion_etablie:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.traiter_message(message)
                else:
                    break
            except:
                break
        
        self.connexion_etablie = False
    
    def traiter_message(self, message):
        if message.startswith("MOVE:"):
            # Format: MOVE:ligne,col
            coords = message.split(":")[1].split(",")
            ligne = int(coords[0])
            col = int(coords[1])
            
            # Jouer le coup
            if self.placer_pion(ligne, col, self.joueur_actuel):
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
                
                if self.verifier_fin_de_jeu():
                    self.game_over = True
                    self.envoyer_message("GAME_OVER")
        
        elif message == "ABANDON":
            self.game_over = True
            self.gagnant = "abandon_adversaire"
    
    def envoyer_message(self, message):
        if self.connexion_etablie and self.client_socket:
            try:
                self.client_socket.send(message.encode())
            except:
                self.connexion_etablie = False
    
    def afficher_ecran_attente(self):
        if self.background_image:
            self.ecran.blit(self.background_image, (0, 0))
        else:
            self.ecran.fill(self.BLANC)
        
        # Police
        try:
            police_titre = pygame.font.Font(self.font_path, int(50 * self.RATIO_X))
            police_info = pygame.font.Font(self.font_path, int(35 * self.RATIO_X))
            police_code = pygame.font.Font(self.font_path, int(60 * self.RATIO_X))
            police_bouton = pygame.font.Font(self.font_path, int(25 * self.RATIO_X))
        except:
            police_titre = pygame.font.Font(None, int(50 * self.RATIO_X))
            police_info = pygame.font.Font(None, int(35 * self.RATIO_X))
            police_code = pygame.font.Font(None, int(60 * self.RATIO_X))
            police_bouton = pygame.font.Font(None, int(25 * self.RATIO_X))
        
        # Titre
        titre = "SALLE D'ATTENTE - HOST"
        surface_titre = police_titre.render(titre, True, self.NOIR)
        rect_titre = surface_titre.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 200))
        self.ecran.blit(surface_titre, rect_titre)
        
        # Code de salon avec bouton copier
        texte_code = f"Code du salon: {self.code_salon}"
        surface_code = police_code.render(texte_code, True, self.BLEU)
        rect_code = surface_code.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 50))
        self.ecran.blit(surface_code, rect_code)
        
        # Bouton copier pour le code
        largeur_bouton_copier = 120
        hauteur_bouton_copier = 40
        self.bouton_copier_code = pygame.Rect(
            rect_code.right + 20,
            rect_code.centery - hauteur_bouton_copier // 2,
            largeur_bouton_copier,
            hauteur_bouton_copier
        )
        
        # Dessiner le bouton copier code
        couleur_bouton = self.VERT if self.pyperclip else self.GRIS
        pygame.draw.rect(self.ecran, couleur_bouton, self.bouton_copier_code, border_radius=10)
        texte_copier = police_bouton.render("Copier", True, self.BLANC)
        rect_texte_copier = texte_copier.get_rect(center=self.bouton_copier_code.center)
        self.ecran.blit(texte_copier, rect_texte_copier)
        
        # IP avec bouton copier
        texte_ip = f"IP: {self.ip_locale}:{self.port}"
        surface_ip = police_info.render(texte_ip, True, self.NOIR)
        rect_ip = surface_ip.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 + 50))
        self.ecran.blit(surface_ip, rect_ip)
        
        # Bouton copier pour l'IP
        self.bouton_copier_ip = pygame.Rect(
            rect_ip.right + 20,
            rect_ip.centery - hauteur_bouton_copier // 2,
            largeur_bouton_copier,
            hauteur_bouton_copier
        )
        
        # Dessiner le bouton copier IP
        pygame.draw.rect(self.ecran, couleur_bouton, self.bouton_copier_ip, border_radius=10)
        surface_copier_ip = police_bouton.render("Copier", True, self.BLANC)
        rect_copier_ip = surface_copier_ip.get_rect(center=self.bouton_copier_ip.center)
        self.ecran.blit(surface_copier_ip, rect_copier_ip)
        
        # Message de confirmation si quelque chose a été copié
        if hasattr(self, 'message_copie') and self.message_copie and hasattr(self, 'temps_copie'):
            temps_ecoule = pygame.time.get_ticks() - self.temps_copie
            if temps_ecoule < 2000:  # Afficher pendant 2 secondes
                alpha = max(0, 255 - (temps_ecoule - 1000) * 255 // 1000) if temps_ecoule > 1000 else 255
                surface_message = police_bouton.render(self.message_copie, True, self.VERT)
                surface_message.set_alpha(alpha)
                rect_message = surface_message.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 + 120))
                self.ecran.blit(surface_message, rect_message)
            else:
                self.message_copie = ""
        
        # Status
        texte_status = "En attente d'un joueur..."
        surface_status = police_info.render(texte_status, True, self.ROUGE)
        rect_status = surface_status.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 + 180))
        self.ecran.blit(surface_status, rect_status)
        
        # Bouton retour
        largeur_bouton = 200
        hauteur_bouton = 60
        self.bouton_retour = pygame.Rect(
            50, 
            self.HAUTEUR - hauteur_bouton - 50,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_retour, border_radius=20)
        texte_retour = police_info.render("Retour", True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour.center)
        self.ecran.blit(texte_retour, rect_texte_retour)


    def get_cases_bloquees_par_pion(self, ligne, col, couleur_case):
        cases_bloquees = []

        if couleur_case == "bleu":
            directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
            for dl, dc in directions:
                nl, nc = ligne + dl, col + dc
                if 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))

        elif couleur_case == "vert":
            mouvements_cavalier = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
            for dl, dc in mouvements_cavalier:
                nl, nc = ligne + dl, col + dc
                if 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))

        elif couleur_case == "jaune":
            directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
            for dl, dc in directions:
                nl, nc = ligne + dl, col + dc
                while 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))
                    if self.plateau[nl][nc] != 0 or self.get_couleur_case(nl, nc) == "jaune":
                        break
                    nl, nc = nl + dl, nc + dc

        elif couleur_case == "rouge":
            directions = [(-1,0), (1,0), (0,-1), (0,1)]
            for dl, dc in directions:
                nl, nc = ligne + dl, col + dc
                while 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))
                    if self.plateau[nl][nc] != 0 or self.get_couleur_case(nl, nc) == "rouge":
                        break
                    nl, nc = nl + dl, nc + dc
                
        return cases_bloquees

    def get_couleur_case(self, ligne, col):
        try:
            with open("plateaux/plateau_18.json", 'r') as f:
                plateau_images = json.load(f)

            # Adapter le plateau si nécessaire
            if len(plateau_images) < 8 or len(plateau_images[0]) < 8:
                plateau_complet = []
                for i in range(8):
                    ligne_data = []
                    for j in range(8):
                        ligne_data.append(plateau_images[i % len(plateau_images)][j % len(plateau_images[0])])
                    plateau_complet.append(ligne_data)
                plateau_images = plateau_complet

            image_path = plateau_images[ligne][col]

            # Déterminer la couleur selon le nom de fichier
            if "rouge" in image_path.lower():
                return "rouge"
            elif "bleu" in image_path.lower():
                return "bleu"
            elif "jaune" in image_path.lower():
                return "jaune"
            elif "vert" in image_path.lower():
                return "vert"
            else:
                return None

        except Exception as e:
            print(f"Erreur lors de la détection de couleur: {e}")
            if (ligne + col) % 4 == 0:
                return "rouge"
            elif (ligne + col) % 4 == 1:
                return "bleu"
            elif (ligne + col) % 4 == 2:
                return "vert"
            else:
                return "jaune"

    def peut_placer_pion(self, ligne, col):
        return (0 <= ligne < 8 and 0 <= col < 8 and 
                self.plateau[ligne][col] == 0 and 
                not self.cases_bloquees[ligne][col])

    def placer_pion(self, ligne, col, joueur):
        if not self.peut_placer_pion(ligne, col):
            return False
            
        self.plateau[ligne][col] = joueur
        
        couleur_case = self.get_couleur_case(ligne, col)
        cases_a_bloquer = self.get_cases_bloquees_par_pion(ligne, col, couleur_case)
        
        for bl, bc in cases_a_bloquer:
            if self.plateau[bl][bc] == 0:
                self.cases_bloquees[bl][bc] = True
                
        return True

    def verifier_fin_de_jeu(self):
        for i in range(8):
            for j in range(8):
                if self.peut_placer_pion(i, j):
                    return False
        return True

    def compter_cases_libres_par_joueur(self):
        cases_libres = 0
        for i in range(8):
            for j in range(8):
                if self.peut_placer_pion(i, j):
                    cases_libres += 1
        return cases_libres

    def run(self):
        if self.pion_blanc and self.pion_noir:
            pion_size = int(self.TAILLE_CASE * 0.8)
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        self.running = True
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.ecran_attente:
                        x, y = event.pos
                        if hasattr(self, 'bouton_retour') and self.bouton_retour.collidepoint(x, y):
                            self.running = False
                            if self.client_socket:
                                self.client_socket.close()
                            if self.server_socket:
                                self.server_socket.close()
                            pygame.quit()
                            import subprocess
                            subprocess.Popen([sys.executable, "menu_principal.py"])
                            sys.exit()
                        elif hasattr(self, 'bouton_copier_code') and self.bouton_copier_code.collidepoint(x, y):
                            if self.pyperclip:
                                self.pyperclip.copy(self.code_salon)
                                self.message_copie = "Code copié !"
                                self.temps_copie = pygame.time.get_ticks()
                        elif hasattr(self, 'bouton_copier_ip') and self.bouton_copier_ip.collidepoint(x, y):
                            if self.pyperclip:
                                self.pyperclip.copy(f"{self.ip_locale}:{self.port}")
                                self.message_copie = "IP copiée !"
                                self.temps_copie = pygame.time.get_ticks()
                    elif not self.game_over and self.joueur_actuel == self.mon_numero:
                        x, y = event.pos
                        if hasattr(self, 'bouton_abandonner') and self.bouton_abandonner.collidepoint(x, y):
                            self.game_over = True
                            self.gagnant = "abandon"
                            self.envoyer_message("ABANDON")
                        else:
                            self.gerer_clic()
                    elif self.game_over:
                        x, y = event.pos
                        if hasattr(self, 'bouton_quitter') and self.bouton_quitter.collidepoint(x, y):
                            self.running = False
                            if self.client_socket:
                                self.client_socket.close()
                            if self.server_socket:
                                self.server_socket.close()
            
            if self.ecran_attente:
                self.afficher_ecran_attente()
            else:
                if self.background_image:
                    self.ecran.blit(self.background_image, (0, 0))
                else:
                    self.ecran.fill(self.BLANC)
                
                self.dessiner_plateau()
                self.afficher_pions()
                self.afficher_cases_bloquees()
                
                if not self.game_over:
                    self.afficher_tour()
                    self.afficher_info_jeu()
                else:
                    self.afficher_fin_de_jeu()
            
            pygame.display.flip()
            clock.tick(60)
        
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        pygame.quit()

    def dessiner_plateau(self):
        try:
            with open("plateaux/plateau_18.json", 'r') as f:
                plateau_images = json.load(f)
            
            if len(plateau_images) < 8 or len(plateau_images[0]) < 8:
                plateau_complet = []
                for i in range(8):
                    ligne = []
                    for j in range(8):
                        ligne.append(plateau_images[i % len(plateau_images)][j % len(plateau_images[0])])
                    plateau_complet.append(ligne)
                plateau_images = plateau_complet
            
            for i in range(8):
                for j in range(8):
                    image_path = plateau_images[i][j]
                    
                    if image_path not in self.images:
                        try:
                            self.images[image_path] = pygame.image.load(image_path).convert_alpha()
                            self.images[image_path] = pygame.transform.scale(self.images[image_path], 
                                                                           (self.TAILLE_CASE, self.TAILLE_CASE))
                        except:
                            couleur = self.get_couleur_case(i, j)
                            surface = pygame.Surface((self.TAILLE_CASE, self.TAILLE_CASE))
                            surface.fill(couleur)
                            self.images[image_path] = surface
                    
                    self.ecran.blit(self.images[image_path], 
                                  (self.OFFSET_X + j * self.TAILLE_CASE, 
                                   self.OFFSET_Y + i * self.TAILLE_CASE))
        except Exception as e:
            print(f"Erreur lors du chargement du plateau: {e}")
            for i in range(8):
                for j in range(8):
                    couleur = self.get_couleur_case(i, j)
                    pygame.draw.rect(self.ecran, couleur, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                     self.OFFSET_Y + i * self.TAILLE_CASE, 
                                     self.TAILLE_CASE, self.TAILLE_CASE))
                    
                    pygame.draw.rect(self.ecran, self.NOIR, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                     self.OFFSET_Y + i * self.TAILLE_CASE, 
                                     self.TAILLE_CASE, self.TAILLE_CASE), 2)

    def afficher_cases_bloquees(self):
        for i in range(8):
            for j in range(8):
                if self.cases_bloquees[i][j]:
                    pygame.draw.rect(self.ecran, self.NOIR, 
                                   (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))

    def afficher_pions(self):
        pion_size = int(self.TAILLE_CASE * 0.8)  
        offset = (self.TAILLE_CASE - pion_size) // 2
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == 1:
                    if self.pion_noir:
                        self.ecran.blit(self.pion_noir,
                                        (self.OFFSET_X + j * self.TAILLE_CASE + offset,
                                         self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                    else:
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2)
                elif self.plateau[i][j] == 2:
                    if self.pion_blanc:
                        self.ecran.blit(self.pion_blanc,
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
                                         pion_size//2, 3)

    def afficher_tour(self):
        try:
            police = pygame.font.Font(self.font_path, int(35 * self.RATIO_X))
        except:
            police = pygame.font.Font(None, int(35 * self.RATIO_X))
            
        if self.joueur_actuel == self.mon_numero:
            texte = "Votre tour - Placez votre pion"
            couleur = self.BLEU
        else:
            texte = "Tour de l'adversaire"
            couleur = self.ROUGE
            
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))
        
        # Afficher qui est qui
        info_joueurs = f"Vous êtes le joueur {self.mon_numero} (HOST)"
        surface_info = police.render(info_joueurs, True, self.NOIR)
        self.ecran.blit(surface_info, (20, 20))

    def afficher_info_jeu(self):
        try:
            police = pygame.font.Font(self.font_path, int(25 * self.RATIO_X))
        except:
            police = pygame.font.Font(None, int(25 * self.RATIO_X))
            
        cases_libres = self.compter_cases_libres_par_joueur()
        texte = f"Cases libres restantes: {cases_libres}"
        surface_texte = police.render(texte, True, self.NOIR)
        self.ecran.blit(surface_texte, (20, self.HAUTEUR - 60))

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

    def afficher_fin_de_jeu(self):
        try:
            police_grand = pygame.font.Font(self.font_path, int(40 * self.RATIO_X))
            police_bouton = pygame.font.Font(self.font_path, int(32 * self.RATIO_X))
        except:
            police_grand = pygame.font.Font(None, int(40 * self.RATIO_X))
            police_bouton = pygame.font.Font(None, int(32 * self.RATIO_X))
            
        if self.gagnant == "abandon":
            texte_principal = "Vous avez abandonne !"
        elif self.gagnant == "abandon_adversaire":
            texte_principal = "L'adversaire a abandonne !"
        else:
            gagnant_nom = "Vous avez" if self.joueur_actuel != self.mon_numero else "L'adversaire"
            texte_principal = f"{gagnant_nom} gagne !"
            
        surface_principale = police_grand.render(texte_principal, True, self.NOIR)
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            self.HAUTEUR // 2 - 500
        ))

        # Bouton Quitter
        largeur_bouton = 250
        hauteur_bouton = 60
        self.bouton_quitter = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton // 2,
            self.HAUTEUR // 2 - -450,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_quitter, border_radius=20)
        texte_quitter = police_bouton.render("Quitter", True, self.BLANC)
        rect_texte_quitter = texte_quitter.get_rect(center=self.bouton_quitter.center)
        self.ecran.blit(texte_quitter, rect_texte_quitter)

    def gerer_clic(self):
        if self.joueur_actuel != self.mon_numero:
            return
            
        pos = pygame.mouse.get_pos()
        
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        if 0 <= ligne < 8 and 0 <= col < 8:
            print(f"Clic sur la case ({ligne}, {col})")
            
            if self.placer_pion(ligne, col, self.joueur_actuel):
                # Envoyer le mouvement au client
                self.envoyer_message(f"MOVE:{ligne},{col}")
                
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1                
                
                if self.verifier_fin_de_jeu():
                    self.game_over = True
                    self.envoyer_message("GAME_OVER")
                    print("Jeu terminé!")                    
            else:
                print("Impossible de placer un pion ici!")

if __name__ == "__main__":
    jeu = Plateau_pion_host()
    jeu.run()