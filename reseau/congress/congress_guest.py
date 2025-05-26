import pygame
import sys
import json
import socket
import threading
import pyperclip
import os

# Répertoire du fichier en cours
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Congress_guest:
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
        pygame.display.set_caption("Congress - GUEST")
        
        # Taille des cases
        self.TAILLE_CASE = int(100 * self.RATIO_X)
        self.OFFSET_X = (self.LARGEUR - 8 * self.TAILLE_CASE) // 2
        self.OFFSET_Y = (self.HAUTEUR - 8 * self.TAILLE_CASE) // 2
        
        # Fond d'écran
        try:
            self.background_image = pygame.image.load("assets/menu-claire/fond-menu-principal.png")
            self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        except:
            self.background_image = None

        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        self.GRIS = (128, 128, 128)
        self.ORANGE = (255, 165, 0)
        self.VERT_PREVIEW = (0, 255, 0, 128)

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
        self.plateau = [[0, 2, 0, 1, 2, 0, 1, 0],
                        [1, 0, 0, 0, 0, 0, 0, 2],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [2, 0, 0, 0, 0, 0, 0, 1],
                        [1, 0, 0, 0, 0, 0, 0, 2],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [2, 0, 0, 0, 0, 0, 0, 1],
                        [0, 1, 0, 2, 1, 0, 2, 0]]
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # État du jeu
        self.game_over = False
        self.gagnant = None
        self.joueur_actuel = 1
        self.mon_numero = 2  # Guest est toujours joueur 2
        self.pion_selectionne = None
        self.mouvements_possibles = []
        
        # Réseau
        self.socket_client = None
        self.connexion_etablie = False
        self.port = 5556
        
        # État de l'écran
        self.ecran_connexion = True
        
        # Champs de saisie
        self.ip_input = ""
        self.code_input = ""
        self.champ_actif = "ip"  # "ip" ou "code"

        self.pyperclip = pyperclip

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
            # Format: MOVE:ligne_dep,col_dep,ligne_arr,col_arr
            coords = message.split(":")[1].split(",")
            ligne_dep = int(coords[0])
            col_dep = int(coords[1])
            ligne_arr = int(coords[2])
            col_arr = int(coords[3])
            
            # Jouer le coup
            self.deplacer_pion((ligne_dep, col_dep), (ligne_arr, col_arr))
            self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
            
            # Vérifier la victoire
            if self.verifier_victoire(1):
                self.game_over = True
                self.gagnant = 1
            elif self.verifier_victoire(2):
                self.game_over = True
                self.gagnant = 2
        
        elif message.startswith("VICTOIRE:"):
            self.game_over = True
            self.gagnant = int(message.split(":")[1])
            
        elif message == "ABANDON":
            self.game_over = True
            self.gagnant = "abandon_adversaire"
    
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
        titre = "REJOINDRE UNE PARTIE"
        surface_titre = police_titre.render(titre, True, self.NOIR)
        rect_titre = surface_titre.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 - 250))
        self.ecran.blit(surface_titre, rect_titre)
        
        # Champ IP
        y_ip = self.HAUTEUR // 2 - 100
        texte_ip = "Adresse IP du host:"
        surface_ip = police_info.render(texte_ip, True, self.NOIR)
        self.ecran.blit(surface_ip, (self.LARGEUR // 2 - 300, y_ip - 40))
        
        # Zone de saisie IP
        rect_ip = pygame.Rect(self.LARGEUR // 2 - 300, y_ip, 600, 50)
        couleur_ip = self.BLEU if self.champ_actif == "ip" else self.GRIS
        pygame.draw.rect(self.ecran, couleur_ip, rect_ip, 3, border_radius=10)
        
        # Texte IP
        surface_ip_input = police_input.render(self.ip_input, True, self.NOIR)
        self.ecran.blit(surface_ip_input, (rect_ip.x + 10, rect_ip.y + 10))
        
        # Champ Code
        y_code = self.HAUTEUR // 2 + 50
        texte_code = "Code du salon:"
        surface_code = police_info.render(texte_code, True, self.NOIR)
        self.ecran.blit(surface_code, (self.LARGEUR // 2 - 300, y_code - 40))
        
        # Zone de saisie Code
        rect_code = pygame.Rect(self.LARGEUR // 2 - 300, y_code, 600, 50)
        couleur_code = self.BLEU if self.champ_actif == "code" else self.GRIS
        pygame.draw.rect(self.ecran, couleur_code, rect_code, 3, border_radius=10)
        
        # Texte Code
        surface_code_input = police_input.render(self.code_input, True, self.NOIR)
        self.ecran.blit(surface_code_input, (rect_code.x + 10, rect_code.y + 10))
        
        # Indication Ctrl+V
        texte_aide = "Utilisez Ctrl+V pour coller"
        surface_aide = police_petit.render(texte_aide, True, self.GRIS)
        rect_aide = surface_aide.get_rect(center=(self.LARGEUR // 2, y_code + 80))
        self.ecran.blit(surface_aide, rect_aide)
        
        # Bouton Connexion
        largeur_bouton = 250
        hauteur_bouton = 60
        self.bouton_connexion = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton // 2,
            self.HAUTEUR // 2 + 200,
            largeur_bouton,
            hauteur_bouton
        )
        
        # Activer le bouton seulement si les deux champs sont remplis
        if self.ip_input and self.code_input:
            pygame.draw.rect(self.ecran, self.VERT, self.bouton_connexion, border_radius=20)
            texte_connexion = police_info.render("Se connecter", True, self.BLANC)
        else:
            pygame.draw.rect(self.ecran, self.GRIS, self.bouton_connexion, border_radius=20)
            texte_connexion = police_info.render("Se connecter", True, self.BLANC)
            
        rect_texte_connexion = texte_connexion.get_rect(center=self.bouton_connexion.center)
        self.ecran.blit(texte_connexion, rect_texte_connexion)
        
        # Bouton retour
        self.bouton_retour = pygame.Rect(
            50, 
            self.HAUTEUR - hauteur_bouton - 50,
            200,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_retour, border_radius=20)
        texte_retour = police_info.render("Retour", True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour.center)
        self.ecran.blit(texte_retour, rect_texte_retour)
        
        # Message d'erreur si nécessaire
        if hasattr(self, 'message_erreur') and self.message_erreur:
            surface_erreur = police_info.render(self.message_erreur, True, self.ROUGE)
            rect_erreur = surface_erreur.get_rect(center=(self.LARGEUR // 2, self.HAUTEUR // 2 + 280))
            self.ecran.blit(surface_erreur, rect_erreur)

    def get_couleur_case(self, ligne, col):
        try:
            with open("plateaux/plateau_19.json", 'r') as f:
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
            # Fallback pattern
            if (ligne + col) % 4 == 0:
                return "rouge"
            elif (ligne + col) % 4 == 1:
                return "bleu"
            elif (ligne + col) % 4 == 2:
                return "vert"
            else:
                return "jaune"

    def get_mouvements_possibles(self, ligne, col):
        mouvements = []
        
        for i in range(8):
            for j in range(8):
                if self.mouvement_valide((ligne, col), (i, j)):
                    mouvements.append((i, j))
        
        return mouvements

    def mouvement_valide(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        # Vérifier si la case d'arrivée est vide
        if self.plateau[ligne_arr][col_arr] != 0:
            return False
        
        # Ne pas permettre de rester sur place
        if ligne_dep == ligne_arr and col_dep == col_arr:
            return False
            
        couleur_case = self.get_couleur_case(ligne_dep, col_dep)
        if not couleur_case:
            return False
        
        # Déterminer les mouvements valides selon la couleur
        if couleur_case == "rouge":  # Tour
            return self.mouvement_tour(ligne_dep, col_dep, ligne_arr, col_arr)
        elif couleur_case == "bleu":  # Roi
            return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1
        elif couleur_case == "jaune":  # Fou
            return self.mouvement_fou(ligne_dep, col_dep, ligne_arr, col_arr)
        elif couleur_case == "vert":  # Cavalier
            return ((abs(ligne_arr - ligne_dep) == 2 and abs(col_arr - col_dep) == 1) or 
                    (abs(ligne_arr - ligne_dep) == 1 and abs(col_arr - col_dep) == 2))
        else:
            return True

    def mouvement_tour(self, ligne_dep, col_dep, ligne_arr, col_arr):
        if ligne_dep != ligne_arr and col_dep != col_arr:
            return False
        
        if ligne_dep == ligne_arr:  # Mouvement horizontal
            direction = 1 if col_arr > col_dep else -1
            col_actuel = col_dep + direction
            
            while col_actuel != col_arr:
                if self.plateau[ligne_dep][col_actuel] != 0:
                    return False
                couleur = self.get_couleur_case(ligne_dep, col_actuel)
                if couleur == "rouge":
                    return False
                col_actuel += direction
                
        else:  # Mouvement vertical
            direction = 1 if ligne_arr > ligne_dep else -1
            ligne_actuel = ligne_dep + direction
            
            while ligne_actuel != ligne_arr:
                if self.plateau[ligne_actuel][col_dep] != 0:
                    return False
                couleur = self.get_couleur_case(ligne_actuel, col_dep)
                if couleur == "rouge":
                    return False
                ligne_actuel += direction
        
        return True

    def mouvement_fou(self, ligne_dep, col_dep, ligne_arr, col_arr):
        if abs(ligne_arr - ligne_dep) != abs(col_arr - col_dep):
            return False
        
        dir_ligne = 1 if ligne_arr > ligne_dep else -1
        dir_col = 1 if col_arr > col_dep else -1
        
        ligne_actuel = ligne_dep + dir_ligne
        col_actuel = col_dep + dir_col
        
        while ligne_actuel != ligne_arr or col_actuel != col_arr:
            if self.plateau[ligne_actuel][col_actuel] != 0:
                return False
            couleur = self.get_couleur_case(ligne_actuel, col_actuel)
            if couleur == "jaune":
                return False
            ligne_actuel += dir_ligne
            col_actuel += dir_col
        
        return True
    
    def deplacer_pion(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
        self.plateau[ligne_dep][col_dep] = 0
    
    def verifier_victoire(self, joueur):
        # Trouver tous les pions du joueur
        positions = []
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == joueur:
                    positions.append((i, j))
        
        if not positions:
            return False
        
        # Vérifier si tous les pions sont connectés
        visites = set()
        pile = [positions[0]]
        
        while pile:
            pos = pile.pop()
            visites.add(pos)
            
            i, j = pos
            for ni, nj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:
                if 0 <= ni < 8 and 0 <= nj < 8 and self.plateau[ni][nj] == joueur and (ni, nj) not in visites:
                    pile.append((ni, nj))
        
        return len(visites) == len(positions)

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
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.ecran_connexion:
                        x, y = event.pos
                        if self.bouton_retour.collidepoint(x, y):
                            self.running = False
                            if self.socket_client:
                                self.socket_client.close()
                            pygame.quit()
                            import subprocess
                            subprocess.Popen([sys.executable, "menu_principal.py"])
                            sys.exit()
                        elif self.bouton_connexion.collidepoint(x, y) and self.ip_input and self.code_input:
                            # Tenter la connexion
                            if self.se_connecter(self.ip_input, self.code_input):
                                self.message_erreur = ""
                            else:
                                self.message_erreur = "Connexion échouée - Vérifiez l'IP et le code"
                        else:
                            # Vérifier quel champ a été cliqué
                            rect_ip = pygame.Rect(self.LARGEUR // 2 - 300, self.HAUTEUR // 2 - 100, 600, 50)
                            rect_code = pygame.Rect(self.LARGEUR // 2 - 300, self.HAUTEUR // 2 + 50, 600, 50)
                            
                            if rect_ip.collidepoint(x, y):
                                self.champ_actif = "ip"
                            elif rect_code.collidepoint(x, y):
                                self.champ_actif = "code"
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
                            if self.socket_client:
                                self.socket_client.close()
                
                elif event.type == pygame.KEYDOWN and self.ecran_connexion:
                    if event.key == pygame.K_TAB:
                        # Basculer entre les champs
                        self.champ_actif = "code" if self.champ_actif == "ip" else "ip"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.champ_actif == "ip":
                            self.ip_input = self.ip_input[:-1]
                        else:
                            self.code_input = self.code_input[:-1]
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Ctrl+V pour coller
                        if self.pyperclip:
                            try:
                                contenu_presse_papier = self.pyperclip.paste()
                                if self.champ_actif == "ip":
                                    # Vérifier si c'est une IP valide avec port
                                    if ":" in contenu_presse_papier:
                                        # Séparer l'IP du port
                                        ip_part = contenu_presse_papier.split(":")[0]
                                        self.ip_input = ip_part[:15]  # Limiter à 15 caractères
                                    else:
                                        # Coller tel quel si c'est juste une IP
                                        self.ip_input = contenu_presse_papier[:15]
                                else:
                                    # Pour le code, garder seulement les caractères alphanumériques
                                    code_propre = ''.join(c for c in contenu_presse_papier if c.isalnum())
                                    self.code_input = code_propre[:6].upper()
                            except:
                                pass
                    elif event.key == pygame.K_RETURN and self.ip_input and self.code_input:
                        # Tenter la connexion avec Entrée
                        if self.se_connecter(self.ip_input, self.code_input):
                            self.message_erreur = ""
                        else:
                            self.message_erreur = "Connexion échouée - Vérifiez l'IP et le code"
                    else:
                        # Ajouter le caractère
                        if self.champ_actif == "ip" and len(self.ip_input) < 15:
                            if event.unicode in "0123456789.":
                                self.ip_input += event.unicode
                        elif self.champ_actif == "code" and len(self.code_input) < 6:
                            if event.unicode.isalnum():
                                self.code_input += event.unicode.upper()
            
            if self.ecran_connexion:
                self.afficher_ecran_connexion()
            else:
                if self.background_image:
                    self.ecran.blit(self.background_image, (0, 0))
                else:
                    self.ecran.fill(self.BLANC)
                
                self.dessiner_plateau()
                self.afficher_preview_mouvements()
                self.afficher_pions()
                self.afficher_pion_selectionne()
                
                if not self.game_over:
                    self.afficher_tour()
                    self.afficher_info_jeu()
                else:
                    self.afficher_fin_de_jeu()
            
            pygame.display.flip()
            clock.tick(60)
        
        if self.socket_client:
            self.socket_client.close()
        pygame.quit()

    def dessiner_plateau(self):
        try:
            with open("plateaux/plateau_19.json", 'r') as f:
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
                            couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
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
                    couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
                    pygame.draw.rect(self.ecran, couleur, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                     self.OFFSET_Y + i * self.TAILLE_CASE, 
                                     self.TAILLE_CASE, self.TAILLE_CASE))

    def afficher_preview_mouvements(self):
        if self.pion_selectionne and self.mouvements_possibles:
            overlay = pygame.Surface((self.TAILLE_CASE, self.TAILLE_CASE), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 100))
            
            for ligne, col in self.mouvements_possibles:
                self.ecran.blit(overlay, 
                              (self.OFFSET_X + col * self.TAILLE_CASE, 
                               self.OFFSET_Y + ligne * self.TAILLE_CASE))
                
                pygame.draw.rect(self.ecran, self.VERT, 
                               (self.OFFSET_X + col * self.TAILLE_CASE, 
                                self.OFFSET_Y + ligne * self.TAILLE_CASE, 
                                self.TAILLE_CASE, self.TAILLE_CASE), 3)

    def afficher_pion_selectionne(self):
        if self.pion_selectionne:
            ligne, col = self.pion_selectionne
            pygame.draw.rect(self.ecran, self.ORANGE, 
                           (self.OFFSET_X + col * self.TAILLE_CASE, 
                            self.OFFSET_Y + ligne * self.TAILLE_CASE, 
                            self.TAILLE_CASE, self.TAILLE_CASE), 5)

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
            texte = "Votre tour - Déplacez un pion"
            couleur = self.BLEU
        else:
            texte = "Tour de l'adversaire"
            couleur = self.ROUGE
            
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))
        
        # Afficher qui est qui
        info_joueurs = f"Vous êtes le joueur {self.mon_numero} (GUEST - Pions {'blancs' if self.mon_numero == 2 else 'noirs'})"
        surface_info = police.render(info_joueurs, True, self.NOIR)
        self.ecran.blit(surface_info, (20, 20))

    def afficher_info_jeu(self):
        try:
            police = pygame.font.Font(self.font_path, int(25 * self.RATIO_X))
        except:
            police = pygame.font.Font(None, int(25 * self.RATIO_X))
            
        # Compter les pions
        pions_noir = sum(1 for i in range(8) for j in range(8) if self.plateau[i][j] == 1)
        pions_blanc = sum(1 for i in range(8) for j in range(8) if self.plateau[i][j] == 2)
        
        texte = f"Pions noirs: {pions_noir} | Pions blancs: {pions_blanc}"
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
            texte_principal = "Vous avez abandonné !"
        elif self.gagnant == "abandon_adversaire":
            texte_principal = "L'adversaire a abandonné !"
        else:
            gagnant_nom = "Vous avez" if self.gagnant == self.mon_numero else "L'adversaire a"
            texte_principal = f"{gagnant_nom} gagné !"
            
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
            self.HAUTEUR // 2 + 450,
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
            if self.pion_selectionne is None:
                # Sélection d'un pion
                if self.plateau[ligne][col] == self.joueur_actuel:
                    self.pion_selectionne = (ligne, col)
                    self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
                    print(f"Pion sélectionné en ({ligne}, {col})")
            else:
                # Déplacement d'un pion
                if self.mouvement_valide(self.pion_selectionne, (ligne, col)):
                    ligne_dep, col_dep = self.pion_selectionne
                    
                    # Envoyer le mouvement au serveur
                    self.envoyer_message(f"MOVE:{ligne_dep},{col_dep},{ligne},{col}")
                    
                    self.deplacer_pion(self.pion_selectionne, (ligne, col))
                    self.pion_selectionne = None
                    self.mouvements_possibles = []
                    self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
                    
                    # Vérifier la victoire
                    if self.verifier_victoire(1):
                        self.game_over = True
                        self.gagnant = 1
                    elif self.verifier_victoire(2):
                        self.game_over = True
                        self.gagnant = 2
                else:
                    # Si on clique sur un autre pion du même joueur
                    if self.plateau[ligne][col] == self.joueur_actuel:
                        self.pion_selectionne = (ligne, col)
                        self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
                    else:
                        # Annuler la sélection
                        self.pion_selectionne = None
                        self.mouvements_possibles = []

if __name__ == "__main__":
    jeu = Congress_guest()
    jeu.run()