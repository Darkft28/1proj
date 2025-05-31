import pygame
import sys
import json
import socket
import threading
import queue  # Pour la queue thread-safe
import sys
import json
import socket
import threading
import queue
import os

def get_theme():
    """Get the current theme from config, fallback to 'Clair' if not found."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'menu', 'user_config.json')
        if not os.path.exists(config_path):
            return "Clair"
        with open(config_path, "r") as f:
            data = json.load(f)
            return data.get("theme", "Clair")
    except:
        return "Clair"


class Plateau_pion:
    def __init__(self, mode_reseau=None, socket_reseau=None, mon_numero=None, connexion_etablie=False):
        pygame.init()
        
        # Paramètres réseau
        self.mode_reseau = mode_reseau  # "host" ou "guest"
        self.socket_reseau = socket_reseau
        self.mon_numero = mon_numero
        self.connexion_etablie = connexion_etablie
        self.network_manager = None  # Sera défini par NetworkManager
        
        # Ajouter un attribut pour tracker l'état de la connexion
        self.adversaire_deconnecte = False
        
        self.font_path = 'assets/police-gloomie_saturday/Gloomie Saturday.otf'
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h

        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440

        # Initialisation de la fenêtre de jeu
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Katarenga")
        
        # Taille des cases pour plateau 10x10
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
                self.VERT: "assets/image_verte.png",
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
                        [10, 0, 0, 0, 0, 0, 0, 0, 0,  10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0,  10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0,  10],
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
        
        # Variables de jeu
        self.joueur_actuel = 1  # 1 pour blanc, 2 pour noir
        self.pion_selectionne = None
        self.mouvements_possibles = []
        self.running = True

        self.tour = 0  # Compteur de tours
        
        # Queue pour les messages réseau (thread-safe)
        self.message_queue = queue.Queue()

    def get_font(self, size):
        """Retourne la police Gloomie Saturday à la taille spécifiée, avec fallback"""
        try:
            return pygame.font.Font(self.font_path, size)
        except:
            return pygame.font.Font(None, size)

    def run(self):
        # Redimensionner les pions
        if self.pion_blanc and self.pion_noir:
            pion_size = int(self.TAILLE_CASE * 0.8)
            offset = (self.TAILLE_CASE - pion_size) // 2
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        # Démarrer le thread de réception des messages réseau si nécessaire
        if self.mode_reseau and self.socket_reseau and self.connexion_etablie:
            thread_recevoir = threading.Thread(target=self.recevoir_messages_reseau)
            thread_recevoir.daemon = True
            thread_recevoir.start()
          # Boucle de jeu
        while self.running:
            # Vérifier la connexion réseau seulement si on est en mode réseau
            if self.mode_reseau and not self.connexion_etablie:
                self.game_over = True
                self.gagnant = "Connexion perdue"
            
            self.ecran.blit(self.background_image, (0, 0))
            self.dessiner_plateau()
            self.afficher_preview_mouvements()
            self.afficher_plateau()
            
            if not self.game_over:
                self.afficher_tour()
                self.afficher_bouton_abandonner()
            else:
                self.afficher_fin_de_jeu()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.mode_reseau and self.socket_reseau:
                        self.envoyer_message("ABANDON")
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if not self.game_over:
                        if hasattr(self, 'bouton_abandonner') and self.bouton_abandonner.collidepoint(x, y):
                            if self.mode_reseau and self.socket_reseau:
                                self.envoyer_message("ABANDON")
                            self.game_over = True
                            self.gagnant = "abandon"
                        else:
                            # En mode réseau, vérifier si c'est notre tour
                            if self.mode_reseau:
                                if self.joueur_actuel == self.mon_numero:
                                    self.gerer_clic()
                            else:
                                self.gerer_clic()
                    else:
                        if self.bouton_rejouer.collidepoint(x, y):
                            self.reinitialiser_jeu()
                        elif self.bouton_quitter.collidepoint(x, y):
                            self.running = False  # Juste arrêter la boucle de jeu
                            pygame.quit()
                            from menu.menu import Menu
                            menu = Menu()
                            menu.executer()
                            return
        
            pygame.display.flip()
        
        # Fermer la connexion réseau si active
        if self.mode_reseau and self.socket_reseau:
            try:
                self.socket_reseau.close()
            except:
                pass
        
        pygame.quit()

    def dessiner_plateau(self):
        try:
            # Utiliser un chemin absolu
            chemin_json = os.path.join(os.path.dirname(__file__), "..", "..", "plateau_final", "plateau_finale.json")
            with open(chemin_json, 'r') as f:
                plateau_images = json.load(f)
                
            # Vérifier que le plateau est 10x10
            if len(plateau_images) != 10 or len(plateau_images[0]) != 10:
                raise Exception("Taille de plateau incorrecte")

            # Dessiner les images du plateau 10x10
            for i in range(10):
                for j in range(10):
                    image_path = plateau_images[i][j]
                    
                    # Convertir le chemin relatif en chemin absolu
                    if not os.path.isabs(image_path):
                        image_path = os.path.join(os.path.dirname(__file__), "..", "..", image_path)
                    
                    # Charger l'image si elle n'est pas déjà en cache
                    if image_path not in self.images:
                        try:
                            self.images[image_path] = pygame.image.load(image_path).convert_alpha()
                            self.images[image_path] = pygame.transform.scale(self.images[image_path], 
                                                                        (self.TAILLE_CASE, self.TAILLE_CASE))
                        except pygame.error as e:
                            print(f"Erreur de chargement de l'image {image_path}: {e}")
                            continue
                    
                    # Dessiner l'image
                    self.ecran.blit(self.images[image_path], 
                                (self.OFFSET_X + j * self.TAILLE_CASE, 
                                self.OFFSET_Y + i * self.TAILLE_CASE))

        except Exception as e:
            print(f"Erreur lors du chargement du plateau: {e}")
            # Fallback: dessiner un damier basique uniquement en cas d'erreur
            for i in range(10):
                for j in range(10):
                    couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
                    pygame.draw.rect(self.ecran, couleur, 
                                   (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))

    def afficher_plateau(self):
        if not self.pion_blanc or not self.pion_noir:
            return
            
        offset = (self.TAILLE_CASE - int(self.TAILLE_CASE * 0.8)) // 2
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == 1:
                    self.ecran.blit(self.pion_blanc, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE + offset, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                elif self.plateau[i][j] == 2:
                    self.ecran.blit(self.pion_noir, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE + offset, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE + offset))

    def afficher_tour(self):
        font = self.get_font(int(36 * self.RATIO_Y))
        texte = f"Tour du joueur {'Blanc' if self.joueur_actuel == 1 else 'Noir'}"
        couleur = self.BLANC if self.joueur_actuel == 1 else self.NOIR
        surface_texte = font.render(texte, True, couleur)
        # Place le texte plus bas (par exemple à 70 pixels)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))

    def afficher_bouton_abandonner(self):
        largeur_bouton = 220
        hauteur_bouton = 50
        police_bouton = self.get_font(25)
        self.bouton_abandonner = pygame.Rect(
            self.LARGEUR - largeur_bouton - 30,
            self.HAUTEUR - hauteur_bouton - 30,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_abandonner, border_radius=20)
        texte_abandonner = police_bouton.render("Abandonner", True, self.BLANC)
        rect_texte_abandonner = texte_abandonner.get_rect(center=self.bouton_abandonner.center)
        self.ecran.blit(texte_abandonner, rect_texte_abandonner)

    def afficher_fin_de_jeu(self):
        police_grand = self.get_font(40)
        texte_principal = "Partie abandonnee" if self.gagnant == "abandon" else f"{self.gagnant} gagne !"
        surface_principale = police_grand.render(texte_principal, True, self.BLANC)
        # Message de victoire au-dessus du plateau
        y_message = self.OFFSET_Y - surface_principale.get_height() - 30
        if y_message < 0:
            y_message = 0
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            y_message
        ))

        # Boutons en bas du plateau (comme Isolation)
        largeur_bouton = 250
        hauteur_bouton = 60
        police_bouton = self.get_font(32)

        # Position Y juste sous le plateau
        y_boutons = self.OFFSET_Y + self.TAILLE_CASE * 10 + 40

        # Bouton Rejouer (bleu)
        self.bouton_rejouer = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton - 20,
            y_boutons,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.BLEU, self.bouton_rejouer, border_radius=20)
        texte_rejouer = police_bouton.render("Rejouer", True, self.BLANC)
        rect_texte_rejouer = texte_rejouer.get_rect(center=self.bouton_rejouer.center)
        self.ecran.blit(texte_rejouer, rect_texte_rejouer)

        # Bouton Quitter
        self.bouton_quitter = pygame.Rect(
            self.LARGEUR // 2 + 20,
            y_boutons,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_quitter, border_radius=20)
        texte_quitter = police_bouton.render("Quitter", True, self.BLANC)
        rect_texte_quitter = texte_quitter.get_rect(center=self.bouton_quitter.center)
        self.ecran.blit(texte_quitter, rect_texte_quitter)

    def afficher_preview_mouvements(self):
        """Affiche des cercles noirs pour les mouvements possibles du pion sélectionné"""
        if self.pion_selectionne and self.mouvements_possibles:
            rayon = self.TAILLE_CASE // 4
            for ligne, col in self.mouvements_possibles:
                centre_x = self.OFFSET_X + col * self.TAILLE_CASE + self.TAILLE_CASE // 2
                centre_y = self.OFFSET_Y + ligne * self.TAILLE_CASE + self.TAILLE_CASE // 2
                pygame.draw.circle(self.ecran, self.NOIR, (centre_x, centre_y), rayon)

    def gerer_clic(self):
        pos = pygame.mouse.get_pos()
        
        # Convertir la position en coordonnées de la grille 10x10
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        # Vérifier si le clic est dans les limites du plateau
        if 0 <= ligne < 10 and 0 <= col < 10:
            if self.pion_selectionne is None:
                # Sélection d'un pion
                if self.plateau[ligne][col] == self.joueur_actuel:
                    # Empêcher la sélection si le pion est dans un camp
                    if (self.joueur_actuel == 1 and (ligne, col) in [(0,0),(0,9)]) or \
                       (self.joueur_actuel == 2 and (ligne, col) in [(9,0),(9,9)]):
                        return  # Ne rien faire, pion dans camp
                    self.pion_selectionne = (ligne, col)
                    self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
            else:
                # Déplacement d'un pion
                if self.mouvement_valide(self.pion_selectionne, (ligne, col)):
                    self.deplacer_pion(self.pion_selectionne, (ligne, col))
                    self.pion_selectionne = None
                    self.mouvements_possibles = []
                    self.joueur_actuel = 3 - self.joueur_actuel  # Alternance entre 1 et 2
                    
                    # Vérifier si un joueur a gagné
                    if self.verifier_victoire(1):
                        self.game_over = True
                        self.gagnant = "Joueur Blanc"
                    elif self.verifier_victoire(2):
                        self.game_over = True
                        self.gagnant = "Joueur Noir"
                else:
                    # Annuler la sélection si le mouvement est invalide
                    self.pion_selectionne = None
                    self.mouvements_possibles = []

    def get_mouvements_possibles(self, ligne, col):
        mouvements = []
        for i in range(len(self.plateau)):
            for j in range(len(self.plateau[0])):
                if self.mouvement_valide((ligne, col), (i, j)):
                    mouvements.append((i, j))
        return mouvements

    def mouvement_valide(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee

        # PREMIER TEST : Vérification des cases marron
        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_images = json.load(f)
            image_dest = plateau_images[ligne_arr][col_arr]
            if "marron" in image_dest.lower():
                return False
        except Exception:
            return False

        # ENSUITE : Les autres vérifications
        # Interdire totalement l'accès aux coins adverses
        if (self.joueur_actuel == 1 and (ligne_arr, col_arr) in [(9,0), (9,9)]) or \
           (self.joueur_actuel == 2 and (ligne_arr, col_arr) in [(0,0), (0,9)]):
            return False

        # Vérifier que la destination n'est pas occupée par un pion allié
        if self.plateau[ligne_arr][col_arr] == self.joueur_actuel:
            return False

        # Vérifier que la destination n'est pas une bordure
        if self.plateau[ligne_arr][col_arr] == 10:
            return False

        # Cas spécial : pion sur la ligne adverse (ligne d'entrée de base)
        pion_sur_ligne_adverse = False
        if (self.joueur_actuel == 1 and ligne_dep == 1) or \
           (self.joueur_actuel == 2 and ligne_dep == 8):
            pion_sur_ligne_adverse = True

            # Peut entrer dans le camp adverse (case 3 pour blanc, 4 pour noir) sans contrainte de couleur
            if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3 and ligne_arr == 0) or \
               (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4 and ligne_arr == 9):
                return True

        # Empêcher d'entrer dans son propre camp (partout sur le plateau)
        if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3) or \
           (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4):
            return False

        # Bloquer complètement l'entrée dans son propre camp (coins)
        if (self.joueur_actuel == 1 and (ligne_arr, col_arr) in [(0,0), (0,9)]) or \
           (self.joueur_actuel == 2 and (ligne_arr, col_arr) in [(9,0), (9,9)]):
            return False

        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_images = json.load(f)

            # Vérifier si les indices sont dans les limites du plateau 10x10
            if ligne_dep >= len(plateau_images) or col_dep >= len(plateau_images[0]):
                return False

            image_path = plateau_images[ligne_dep][col_dep]
            image_dest = plateau_images[ligne_arr][col_arr]
            if "marron" in image_dest.lower():
                return False

            if "rouge" in image_path.lower():
                if not (ligne_arr == ligne_dep or col_arr == col_dep) or (ligne_arr == ligne_dep and col_arr == col_dep):
                    return False
                # Mouvement horizontal (gauche/droite)
                if ligne_arr == ligne_dep:
                    step = 1 if col_arr > col_dep else -1
                    c = col_dep + step
                    while c != col_arr + step:
                        if self.plateau[ligne_dep][c] != 0 and c != col_arr:
                            return False
                        img = plateau_images[ligne_dep][c]
                        if "rouge" in img.lower():
                            # On ne peut pas aller après la première rouge rencontrée
                            return c == col_arr
                        if c == col_arr:
                            break
                        c += step
                # Mouvement vertical (haut/bas)
                else:
                    step = 1 if ligne_arr > ligne_dep else -1
                    l = ligne_dep + step
                    while l != ligne_arr + step:
                        if self.plateau[l][col_dep] != 0 and l != ligne_arr:
                            return False
                        img = plateau_images[l][col_dep]
                        if "rouge" in img.lower():
                            return l == ligne_arr
                        if l == ligne_arr:
                            break
                        l += step
                return True
            elif "bleu" in image_path.lower():
                # Mouvement de roi (une case dans toutes les directions)
                return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1 and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "jaune" in image_path.lower():
                # Mouvement en diagonale
                if abs(ligne_arr - ligne_dep) != abs(col_arr - col_dep) or (ligne_arr == ligne_dep and col_arr == col_dep):
                    return False
                step_l = 1 if ligne_arr > ligne_dep else -1
                step_c = 1 if col_arr > col_dep else -1
                l, c = ligne_dep + step_l, col_dep + step_c
                while (l != ligne_arr + step_l) and (c != col_arr + step_c):
                    if self.plateau[l][c] != 0 and (l, c) != (ligne_arr, col_arr):
                        return False
                    img = plateau_images[l][c]
                    if "jaune" in img.lower():
                        # On ne peut pas aller après la première jaune rencontrée
                        return l == ligne_arr and c == col_arr
                    if l == ligne_arr and c == col_arr:
                        break
                    l += step_l
                    c += step_c
                return True
            elif "vert" in image_path.lower():
                # Mouvement de cavalier
                return (abs(ligne_arr - ligne_dep) == 2 and abs(col_arr - col_dep) == 1) or \
                       (abs(ligne_arr - ligne_dep) == 1 and abs(col_arr - col_dep) == 2)
            else:
                # Mouvement libre pour les autres cases
                return True

        except Exception as e:
            return False

    def deplacer_pion(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee

        pion_entre_dans_camp = False
        if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3) or \
           (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4):
            pion_entre_dans_camp = True

        # Bloquer la capture au premier tour de chaque joueur
        if self.tour < 2 and self.plateau[ligne_arr][col_arr] in [1, 2]:
            return False

        # Capturer le pion
        if self.plateau[ligne_arr][col_arr] in [1, 2] and not pion_entre_dans_camp:
            pion_capture = self.plateau[ligne_arr][col_arr]

        # Déplacer le pion
        if pion_entre_dans_camp:
            self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]  # Ajoute cette ligne !
            self.plateau[ligne_dep][col_dep] = 0
        else:
            self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
            self.plateau[ligne_dep][col_dep] = 0

        self.tour += 1  # Incrémente le nombre de tours
        return True

    def verifier_victoire(self, joueur):
        # Pour les blancs (joueur 1), camps adverses = (0,0) et (0,9)
        # Pour les noirs (joueur 2), camps adverses = (9,0) et (9,9)
        if joueur == 1:
            camps = [(0, 0), (0, 9)]
            adversaire = 2
        else:
            camps = [(9, 0), (9, 9)]
            adversaire = 1

        # Victoire si les deux camps adverses sont occupés par un pion du joueur
        if all(self.plateau[i][j] == joueur for i, j in camps):
            return True

        # Victoire si l'adversaire n'a plus de pions
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == adversaire:
                    return False
        return True

    def reinitialiser_jeu(self):
        # Remettre le plateau et les variables à l'état initial
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
        self.pion_selectionne = None
        self.mouvements_possibles = []
        self.joueur_actuel = 1
        self.game_over = False
        self.gagnant = None

    def recevoir_messages_reseau(self):
        """Thread pour recevoir les messages réseau"""
        while self.connexion_etablie and self.socket_reseau:
            try:
                message = self.socket_reseau.recv(1024).decode()
                if message:
                    self.traiter_message_reseau(message)
                else:
                    break
            except:
                break
        self.connexion_etablie = False

    def traiter_message_reseau(self, message):
        """Traite les messages reçus du réseau"""
        # Mettre le message dans la queue pour traitement dans le thread principal
        self.message_queue.put(message)

    def traiter_messages_queue(self):
        """Traite les messages de la queue dans le thread principal (thread-safe)"""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                
                if message.startswith("MOVE:"):
                    # Format: MOVE:ligne_dep,col_dep,ligne_arr,col_arr
                    coords = message.split(":")[1].split(",")
                    ligne_dep, col_dep, ligne_arr, col_arr = map(int, coords)
                    
                    # Appliquer le mouvement de l'adversaire
                    if self.deplacer_pion((ligne_dep, col_dep), (ligne_arr, col_arr)):
                        # Changer de joueur
                        self.joueur_actuel = 1 if self.joueur_actuel == 2 else 2
                        
                elif message.startswith("VICTOIRE:"):
                    self.game_over = True
                    gagnant_numero = int(message.split(":")[1])
                    if gagnant_numero == self.mon_numero:
                        self.gagnant = "Vous"
                    else:
                        self.gagnant = "Adversaire"
                        
                elif message == "ABANDON":
                    self.game_over = True
                    self.gagnant = "Adversaire a abandonné"
        except queue.Empty:
            pass

    def envoyer_message(self, message):
        """Envoie un message via le réseau"""
        if self.mode_reseau and self.socket_reseau and self.connexion_etablie:
            try:
                self.socket_reseau.send(message.encode())
            except:
                self.connexion_etablie = False

# Lancement du jeu
if __name__ == "__main__":
    jeu = Plateau_pion()
    jeu.run()

