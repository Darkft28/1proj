# filepath: c:\Users\robin\Desktop\supinfo\1proj\1proj\reseau\Katarenga\plateau_pion_guest.py
import pygame
import sys
import json
import socket
import threading
import pyperclip
import os
from menu.config import get_theme

# Répertoire du fichier en cours
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Plateau_pion_guest:
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
        pygame.display.set_caption("Katarenga - GUEST")
        
        # Taille des cases pour plateau 10x10
        self.TAILLE_CASE = int(100 * self.RATIO_X)  # Plus petit pour 10x10
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
        self.ROUGE_CLAIR = (255, 100, 100)

        # Images du plateau
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
                
            # Images spécifiques Katarenga
            self.image_bordure = pygame.image.load("assets/bordure.png").convert_alpha()
            self.image_coin = pygame.image.load("assets/coin.png").convert_alpha()
        except pygame.error as e:
            print(f"Erreur lors du chargement des images: {e}")

        # Pions
        try:
            self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
            self.pion_noir = pygame.image.load("assets/pion_noir.png")
        except:
            self.pion_blanc = None
            self.pion_noir = None

        # Plateau 10x10 pour Katarenga
        self.plateau = [[0 for _ in range(10)] for _ in range(10)]
        self.plateau_images = []
        self.charger_plateau_katarenga()
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # État du jeu Katarenga
        self.game_over = False
        self.gagnant = None
        self.joueur_actuel = 1
        self.mon_numero = 2  # Guest est toujours joueur 2
        
        # Positions des pions Katarenga
        self.position_joueur1 = (1, 1)  # Position initiale joueur 1
        self.position_joueur2 = (8, 8)  # Position initiale joueur 2
        self.plateau[1][1] = 1
        self.plateau[8][8] = 2
        
        # Réseau
        self.socket_client = None
        self.connexion_etablie = False
        self.port = 5555
        
        # État de l'écran
        self.ecran_connexion = True
        
        # Champs de saisie
        self.ip_input = ""
        self.code_input = ""
        self.champ_actif = "ip"  # "ip" ou "code"

        self.pyperclip = pyperclip

    def charger_plateau_katarenga(self):
        """Charge le plateau Katarenga 10x10"""
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
                self.plateau_images = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement du plateau Katarenga: {e}")
            # Créer un plateau par défaut si le fichier n'existe pas
            self.plateau_images = [["assets/image_rouge.png" for _ in range(10)] for _ in range(10)]

    def se_connecter(self, ip_host, code_salon):
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect((ip_host, self.port))
            
            # Recevoir le code de salon du serveur
            code_serveur = self.socket_client.recv(1024).decode()
            
            # Vérifier le code
            if code_serveur == code_salon:
                self.socket_client.send("OK".encode())
                self.connexion_etablie = True
                self.ecran_connexion = False
                
                # Thread pour recevoir les messages
                thread_recevoir = threading.Thread(target=self.recevoir_messages)
                thread_recevoir.daemon = True
                thread_recevoir.start()
                
                return True
            else:
                self.socket_client.close()
                return False
                
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            if self.socket_client:
                self.socket_client.close()
            return False
    
    def recevoir_messages(self):
        while self.connexion_etablie:
            try:
                message = self.socket_client.recv(1024).decode()
                if message:
                    self.traiter_message(message)
                else:
                    break
            except:
                break
        
        self.connexion_etablie = False
    
    def traiter_message(self, message):
        if message.startswith("MOVE:"):
            # Format: MOVE:from_ligne,from_col,to_ligne,to_col
            coords = message.split(":")[1].split(",")
            from_ligne = int(coords[0])
            from_col = int(coords[1])
            to_ligne = int(coords[2])
            to_col = int(coords[3])
            
            # Appliquer le mouvement
            if self.deplacer_pion(from_ligne, from_col, to_ligne, to_col, self.joueur_actuel):
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
                
                if self.verifier_victoire():
                    self.game_over = True
        
        elif message == "ABANDON":
            self.game_over = True
            self.gagnant = "abandon_adversaire"
            
        elif message == "GAME_OVER":
            self.game_over = True
    
    def envoyer_message(self, message):
        if self.connexion_etablie and self.socket_client:
            try:
                self.socket_client.send(message.encode())
            except:
                self.connexion_etablie = False
    
    def afficher_ecran_connexion(self):
        if self.background_image:
            self.ecran.blit(self.background_image, (0, 0))
        else:
            self.ecran.fill(self.BLANC)
        
        # Police
        try:
            police_titre = pygame.font.Font(self.font_path, int(50 * self.RATIO_X))
            police_info = pygame.font.Font(self.font_path, int(35 * self.RATIO_X))
            police_input = pygame.font.Font(self.font_path, int(30 * self.RATIO_X))
            police_petit = pygame.font.Font(self.font_path, int(20 * self.RATIO_X))
        except:
            police_titre = pygame.font.Font(None, int(50 * self.RATIO_X))
            police_info = pygame.font.Font(None, int(35 * self.RATIO_X))
            police_input = pygame.font.Font(None, int(30 * self.RATIO_X))
            police_petit = pygame.font.Font(None, int(20 * self.RATIO_X))
        
        # Titre
        titre = "REJOINDRE UNE PARTIE KATARENGA"
        surface_titre = police_titre.render(titre, True, self.NOIR)
        rect_titre = surface_titre.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 250))
        self.ecran.blit(surface_titre, rect_titre)
        
        # Champ IP
        rect_ip = pygame.Rect(self.LARGEUR // 2 - 200, self.HAUTEUR // 2 - 150, 400, 50)
        couleur_ip = self.VERT if self.champ_actif == "ip" else self.GRIS
        pygame.draw.rect(self.ecran, self.BLANC, rect_ip)
        pygame.draw.rect(self.ecran, couleur_ip, rect_ip, 3)
        
        texte_ip = police_input.render(self.ip_input, True, self.NOIR)
        self.ecran.blit(texte_ip, (rect_ip.x + 10, rect_ip.y + 10))
        
        label_ip = police_info.render("Adresse IP de l'hôte:", True, self.NOIR)
        self.ecran.blit(label_ip, (rect_ip.x, rect_ip.y - 40))
        
        # Champ Code
        rect_code = pygame.Rect(self.LARGEUR // 2 - 200, self.HAUTEUR // 2 - 50, 400, 50)
        couleur_code = self.VERT if self.champ_actif == "code" else self.GRIS
        pygame.draw.rect(self.ecran, self.BLANC, rect_code)
        pygame.draw.rect(self.ecran, couleur_code, rect_code, 3)
        
        texte_code = police_input.render(self.code_input, True, self.NOIR)
        self.ecran.blit(texte_code, (rect_code.x + 10, rect_code.y + 10))
        
        label_code = police_info.render("Code de la partie:", True, self.NOIR)
        self.ecran.blit(label_code, (rect_code.x, rect_code.y - 40))
        
        # Bouton Connexion
        self.bouton_connexion = pygame.Rect(self.LARGEUR // 2 - 100, self.HAUTEUR // 2 + 50, 200, 60)
        pygame.draw.rect(self.ecran, self.VERT, self.bouton_connexion, border_radius=15)
        texte_connexion = police_info.render("Se connecter", True, self.BLANC)
        rect_texte = texte_connexion.get_rect(center=self.bouton_connexion.center)
        self.ecran.blit(texte_connexion, rect_texte)
        
        # Bouton Retour
        self.bouton_retour = pygame.Rect(50, 50, 120, 40)
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_retour, border_radius=15)
        texte_retour = police_input.render("Retour", True, self.BLANC)
        rect_retour = texte_retour.get_rect(center=self.bouton_retour.center)
        self.ecran.blit(texte_retour, rect_retour)

    def mouvement_valide_katarenga(self, from_ligne, from_col, to_ligne, to_col, joueur):
        """Vérifie si un mouvement Katarenga est valide"""
        # Vérifier que la position de départ contient le bon pion
        if self.plateau[from_ligne][from_col] != joueur:
            return False
            
        # Vérifier que la destination est libre et dans les limites
        if not (0 <= to_ligne < 10 and 0 <= to_col < 10):
            return False
        if self.plateau[to_ligne][to_col] != 0:
            return False
            
        # Mouvement en diagonale uniquement
        diff_ligne = abs(to_ligne - from_ligne)
        diff_col = abs(to_col - from_col)
        
        if diff_ligne != diff_col or diff_ligne == 0:
            return False
            
        # Vérifier qu'il n'y a pas d'obstacles sur le chemin
        step_ligne = 1 if to_ligne > from_ligne else -1
        step_col = 1 if to_col > from_col else -1
        
        check_ligne = from_ligne + step_ligne
        check_col = from_col + step_col
        
        while check_ligne != to_ligne and check_col != to_col:
            if self.plateau[check_ligne][check_col] != 0:
                return False
            check_ligne += step_ligne
            check_col += step_col
            
        return True

    def deplacer_pion(self, from_ligne, from_col, to_ligne, to_col, joueur):
        """Déplace un pion selon les règles de Katarenga"""
        if not self.mouvement_valide_katarenga(from_ligne, from_col, to_ligne, to_col, joueur):
            return False
            
        # Effectuer le déplacement
        self.plateau[from_ligne][from_col] = 0
        self.plateau[to_ligne][to_col] = joueur
        
        # Mettre à jour la position du joueur
        if joueur == 1:
            self.position_joueur1 = (to_ligne, to_col)
        else:
            self.position_joueur2 = (to_ligne, to_col)
            
        return True

    def verifier_victoire(self):
        """Vérifie les conditions de victoire de Katarenga"""
        # Victoire par atteinte du coin opposé
        if self.position_joueur1 == (8, 8):  # Joueur 1 atteint le coin opposé
            self.gagnant = 1
            return True
        if self.position_joueur2 == (1, 1):  # Joueur 2 atteint le coin opposé
            self.gagnant = 2
            return True
            
        # Victoire par blocage de l'adversaire
        if not self.a_mouvements_possibles(1):
            self.gagnant = 2
            return True
        if not self.a_mouvements_possibles(2):
            self.gagnant = 1
            return True
            
        return False

    def a_mouvements_possibles(self, joueur):
        """Vérifie si un joueur a des mouvements possibles"""
        if joueur == 1:
            from_ligne, from_col = self.position_joueur1
        else:
            from_ligne, from_col = self.position_joueur2
            
        # Tester tous les mouvements diagonaux possibles
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for d_ligne, d_col in directions:
            for distance in range(1, 10):
                to_ligne = from_ligne + d_ligne * distance
                to_col = from_col + d_col * distance
                
                if self.mouvement_valide_katarenga(from_ligne, from_col, to_ligne, to_col, joueur):
                    return True
                    
        return False

    def dessiner_plateau(self):
        """Dessine le plateau 10x10 de Katarenga"""
        for ligne in range(10):
            for col in range(10):
                x = self.OFFSET_X + col * self.TAILLE_CASE
                y = self.OFFSET_Y + ligne * self.TAILLE_CASE
                
                # Dessiner l'image de la case
                try:
                    image_path = self.plateau_images[ligne][col]
                    
                    if "bordure" in image_path:
                        image = pygame.transform.scale(self.image_bordure, (self.TAILLE_CASE, self.TAILLE_CASE))
                    elif "coin" in image_path:
                        image = pygame.transform.scale(self.image_coin, (self.TAILLE_CASE, self.TAILLE_CASE))
                    else:
                        # Déterminer la couleur de base
                        if "rouge" in image_path.lower():
                            couleur = self.ROUGE
                        elif "bleu" in image_path.lower():
                            couleur = self.BLEU
                        elif "jaune" in image_path.lower():
                            couleur = self.JAUNE
                        elif "vert" in image_path.lower():
                            couleur = self.VERT
                        else:
                            couleur = self.BLANC
                            
                        if couleur in self.images:
                            image = pygame.transform.scale(self.images[couleur], (self.TAILLE_CASE, self.TAILLE_CASE))
                        else:
                            image = pygame.Surface((self.TAILLE_CASE, self.TAILLE_CASE))
                            image.fill(couleur)
                    
                    self.ecran.blit(image, (x, y))
                    
                except:
                    # Fallback: couleur unie
                    pygame.draw.rect(self.ecran, self.BLANC, (x, y, self.TAILLE_CASE, self.TAILLE_CASE))
                
                # Dessiner la bordure de la case
                pygame.draw.rect(self.ecran, self.NOIR, (x, y, self.TAILLE_CASE, self.TAILLE_CASE), 1)

    def dessiner_pions(self):
        """Dessine les pions sur le plateau"""
        pion_size = int(self.TAILLE_CASE * 0.8)
        
        for ligne in range(10):
            for col in range(10):
                if self.plateau[ligne][col] != 0:
                    x = self.OFFSET_X + col * self.TAILLE_CASE + (self.TAILLE_CASE - pion_size) // 2
                    y = self.OFFSET_Y + ligne * self.TAILLE_CASE + (self.TAILLE_CASE - pion_size) // 2
                    
                    if self.plateau[ligne][col] == 1:
                        if self.pion_blanc:
                            pion = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
                            self.ecran.blit(pion, (x, y))
                        else:
                            pygame.draw.circle(self.ecran, self.BLANC, 
                                             (x + pion_size//2, y + pion_size//2), pion_size//2)
                    elif self.plateau[ligne][col] == 2:
                        if self.pion_noir:
                            pion = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
                            self.ecran.blit(pion, (x, y))
                        else:
                            pygame.draw.circle(self.ecran, self.NOIR, 
                                             (x + pion_size//2, y + pion_size//2), pion_size//2)

    def dessiner_interface(self):
        """Dessine l'interface de jeu"""
        try:
            police_info = pygame.font.Font(self.font_path, int(30 * self.RATIO_X))
            police_bouton = pygame.font.Font(self.font_path, int(25 * self.RATIO_X))
        except:
            police_info = pygame.font.Font(None, int(30 * self.RATIO_X))
            police_bouton = pygame.font.Font(None, int(25 * self.RATIO_X))
        
        # Afficher le joueur actuel
        if self.joueur_actuel == self.mon_numero:
            texte_tour = "À votre tour"
            couleur_tour = self.VERT
        else:
            texte_tour = "Tour de l'adversaire"
            couleur_tour = self.ROUGE
            
        surface_tour = police_info.render(texte_tour, True, couleur_tour)
        self.ecran.blit(surface_tour, (50, self.HAUTEUR - 150))
        
        # Bouton Abandon
        self.bouton_abandon = pygame.Rect(self.LARGEUR - 200, 50, 150, 50)
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_abandon, border_radius=15)
        texte_abandon = police_bouton.render("Abandonner", True, self.BLANC)
        rect_abandon = texte_abandon.get_rect(center=self.bouton_abandon.center)
        self.ecran.blit(texte_abandon, rect_abandon)

    def dessiner_jeu(self):
        """Dessine le jeu complet"""
        if self.background_image:
            self.ecran.blit(self.background_image, (0, 0))
        else:
            self.ecran.fill(self.BLANC)
            
        self.dessiner_plateau()
        self.dessiner_pions()
        self.dessiner_interface()

    def afficher_fin_de_jeu(self):
        """Affiche l'écran de fin de jeu"""
        if self.background_image:
            self.ecran.blit(self.background_image, (0, 0))
        else:
            self.ecran.fill(self.BLANC)
        
        try:
            police_grand = pygame.font.Font(self.font_path, int(40 * self.RATIO_X))
            police_bouton = pygame.font.Font(self.font_path, int(32 * self.RATIO_X))
        except:
            police_grand = pygame.font.Font(None, int(40 * self.RATIO_X))
            police_bouton = pygame.font.Font(None, int(32 * self.RATIO_X))
            
        if self.gagnant == "abandon":
            texte_principal = "Vous avez abandonné !"
        elif self.gagnant == "abandon_adversaire":
            texte_principal = "L'adversaire a abandonné !"
        elif self.gagnant == self.mon_numero:
            texte_principal = "Vous avez gagné !"
        else:
            texte_principal = "L'adversaire a gagné !"
            
        surface_principale = police_grand.render(texte_principal, True, self.NOIR)
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            self.HAUTEUR // 2 - 100
        ))

        # Bouton Quitter
        largeur_bouton = 250
        hauteur_bouton = 60
        self.bouton_quitter = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton // 2,
            self.HAUTEUR // 2 + 50,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_quitter, border_radius=20)
        texte_quitter = police_bouton.render("Quitter", True, self.BLANC)
        rect_texte_quitter = texte_quitter.get_rect(center=self.bouton_quitter.center)
        self.ecran.blit(texte_quitter, rect_texte_quitter)

    def gerer_clic_jeu(self, pos):
        """Gère les clics pendant le jeu"""
        if self.joueur_actuel != self.mon_numero:
            return
            
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        if 0 <= ligne < 10 and 0 <= col < 10:
            # Obtenir la position actuelle du joueur
            if self.mon_numero == 1:
                from_ligne, from_col = self.position_joueur1
            else:
                from_ligne, from_col = self.position_joueur2
                
            # Tenter le déplacement
            if self.deplacer_pion(from_ligne, from_col, ligne, col, self.mon_numero):
                # Envoyer le mouvement au serveur
                self.envoyer_message(f"MOVE:{from_ligne},{from_col},{ligne},{col}")
                
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
                
                if self.verifier_victoire():
                    self.game_over = True
                    self.envoyer_message("GAME_OVER")

    def run(self):
        if self.pion_blanc and self.pion_noir:
            pion_size = int(self.TAILLE_CASE * 0.8)
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        self.running = True
        clock = pygame.time.Clock()
        self.message_erreur = ""
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.connexion_etablie:
                        self.envoyer_message("ABANDON")
                    self.running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.ecran_connexion:
                        pos = pygame.mouse.get_pos()
                        
                        # Gestion des clics sur l'écran de connexion
                        if self.bouton_connexion.collidepoint(pos):
                            if self.ip_input and self.code_input:
                                if self.se_connecter(self.ip_input, self.code_input):
                                    print("Connexion réussie!")
                                else:
                                    print("Échec de la connexion")
                                    
                        elif self.bouton_retour.collidepoint(pos):
                            self.running = False
                            
                        # Clic sur les champs de saisie
                        rect_ip = pygame.Rect(self.LARGEUR // 2 - 200, self.HAUTEUR // 2 - 150, 400, 50)
                        rect_code = pygame.Rect(self.LARGEUR // 2 - 200, self.HAUTEUR // 2 - 50, 400, 50)
                        
                        if rect_ip.collidepoint(pos):
                            self.champ_actif = "ip"
                        elif rect_code.collidepoint(pos):
                            self.champ_actif = "code"
                            
                    elif self.game_over:
                        pos = pygame.mouse.get_pos()
                        if hasattr(self, 'bouton_quitter') and self.bouton_quitter.collidepoint(pos):
                            self.running = False
                            
                    else:
                        pos = pygame.mouse.get_pos()
                        
                        # Bouton abandon
                        if hasattr(self, 'bouton_abandon') and self.bouton_abandon.collidepoint(pos):
                            self.game_over = True
                            self.gagnant = "abandon"
                            self.envoyer_message("ABANDON")
                        else:
                            self.gerer_clic_jeu(pos)
                            
                elif event.type == pygame.KEYDOWN and self.ecran_connexion:
                    if event.key == pygame.K_TAB:
                        self.champ_actif = "code" if self.champ_actif == "ip" else "ip"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.champ_actif == "ip":
                            self.ip_input = self.ip_input[:-1]
                        else:
                            self.code_input = self.code_input[:-1]
                    elif event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        try:
                            texte_colle = self.pyperclip.paste()
                            if self.champ_actif == "ip":
                                self.ip_input += texte_colle
                            else:
                                self.code_input += texte_colle
                        except:
                            pass
                    elif event.unicode.isprintable():
                        if self.champ_actif == "ip":
                            self.ip_input += event.unicode
                        else:
                            self.code_input += event.unicode
            
            # Affichage
            if self.ecran_connexion:
                self.afficher_ecran_connexion()
            elif self.game_over:
                self.afficher_fin_de_jeu()
            else:
                self.dessiner_jeu()
                
            pygame.display.flip()
            clock.tick(60)
        
        # Nettoyage
        if self.connexion_etablie and self.socket_client:
            self.socket_client.close()
        pygame.quit()

if __name__ == "__main__":
    jeu = Plateau_pion_guest()
    jeu.run()
