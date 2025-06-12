import pygame
import sys
import json
import random
import time
from menu.config import get_theme

class Plateau_pion:
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
        pygame.display.set_caption("Katarenga - Joueur VS IA")
        
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
        
        # Configuration IA
        self.joueur_humain = 1  # Le joueur humain joue avec les pions blancs
        self.joueur_ia = 2      # L'IA joue avec les pions noirs
        self.delai_ia = 2000    # Délai en millisecondes avant que l'IA joue
        self.temps_derniere_action = 0
        
        # Variables de jeu
        self.pion_selectionne = None
        self.mouvements_possibles = []
        self.running = True
        self.bouton_abandonner = None
        self.bouton_rejouer = None
        self.bouton_quitter = None

    def pion_dans_camp_adverse(self, ligne, col, joueur):
        """Vérifie si un pion est dans le camp adverse"""
        if joueur == 1:  # Joueur blanc
            # Camp adverse = coins noirs (9,0) et (9,9)
            return (ligne, col) in [(9, 0), (9, 9)]
        else:  # Joueur noir (IA)
            # Camp adverse = coins blancs (0,0) et (0,9)
            return (ligne, col) in [(0, 0), (0, 9)]

    def dessiner_plateau(self):
        """Dessine le plateau de jeu avec les images"""
        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
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
                    couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
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
                if self.plateau[i][j] == 1:  # Pion blanc (joueur humain)
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
                    
                    # Ajouter un indicateur visuel pour les pions bloqués dans le camp adverse
                    if self.pion_dans_camp_adverse(i, j, 1):
                        # Dessiner un cercle rouge autour du pion pour indiquer qu'il est bloqué
                        pygame.draw.circle(self.ecran, self.ROUGE,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2 + 5, 3)
                        
                elif self.plateau[i][j] == 2:  # Pion noir (IA)
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
                    
                    # Ajouter un indicateur visuel pour les pions bloqués dans le camp adverse
                    if self.pion_dans_camp_adverse(i, j, 2):
                        # Dessiner un cercle rouge autour du pion pour indiquer qu'il est bloqué
                        pygame.draw.circle(self.ecran, self.ROUGE,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2 + 5, 3)

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

    def afficher_tour(self):
        """Affiche le tour actuel"""
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 35)
        if self.joueur_actuel == self.joueur_humain:
            texte = "Votre tour - Deplacez vos pions"
            couleur = self.NOIR
        else:
            texte = "L'ordinateur reflechit..."
            couleur = self.BLANC
        
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))

    def mouvement_valide(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee

        # NOUVEAU : Vérifier si le pion de départ est dans un camp adverse
        if self.pion_dans_camp_adverse(ligne_dep, col_dep, self.joueur_actuel):
            return False  # Les pions dans le camp adverse ne peuvent plus bouger

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

    def get_mouvements_possibles(self, ligne, col):
        """Retourne tous les mouvements possibles pour un pion donné"""
        # Si le pion est dans un camp adverse, il ne peut plus bouger
        if self.pion_dans_camp_adverse(ligne, col, self.plateau[ligne][col]):
            return []
        
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
            # Mettre à jour la case d'arrivée avant de vider la case de départ
            self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
            self.plateau[ligne_dep][col_dep] = 0
        else:
            # Déplacement normal
            self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
            self.plateau[ligne_dep][col_dep] = 0

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

    def jouer_ia(self):
        """IA simple qui choisit un mouvement aléatoire parmi les possibles"""
        # Trouver tous les pions de l'IA qui peuvent encore bouger
        pions_ia = []
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == self.joueur_ia:
                    # Vérifier si le pion peut encore bouger (pas dans un camp adverse)
                    if not self.pion_dans_camp_adverse(i, j, self.joueur_ia):
                        pions_ia.append((i, j))
        
        if not pions_ia:
            return False
        
        # Mélanger les pions pour un comportement aléatoire
        random.shuffle(pions_ia)
        
        # Essayer de trouver un mouvement valide
        for pion in pions_ia:
            mouvements = self.get_mouvements_possibles(*pion)
            if mouvements:
                # Choisir un mouvement aléatoire
                depart = pion
                arrivee = random.choice(mouvements)
                self.deplacer_pion(depart, arrivee)
                
                # Vérifier victoire
                if self.verifier_victoire(self.joueur_ia):
                    self.game_over = True
                    self.gagnant = "IA"
                
                return True
        
        return False

    def afficher_info_jeu(self):
        """Affiche les informations du jeu et le bouton abandonner"""
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 25)
        
        # Compter les pions
        pions_joueur = 0
        pions_ia = 0
        pions_joueur_bloques = 0
        pions_ia_bloques = 0
        
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == 1:
                    pions_joueur += 1
                    if self.pion_dans_camp_adverse(i, j, 1):
                        pions_joueur_bloques += 1
                elif self.plateau[i][j] == 2:
                    pions_ia += 1
                    if self.pion_dans_camp_adverse(i, j, 2):
                        pions_ia_bloques += 1
        
        texte = f"Vos pions: {pions_joueur} (bloques: {pions_joueur_bloques}) | Pions IA: {pions_ia} (bloques: {pions_ia_bloques})"
        surface_texte = police.render(texte, True, self.NOIR)
        self.ecran.blit(surface_texte, (20, self.HAUTEUR - 60))

        # Bouton abandonner 
        if not self.game_over:
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
        """Affiche l'écran de fin de jeu"""
        police_grand = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        
        # Message de victoire au-dessus du plateau
        if self.gagnant == "abandon":
            texte_principal = "Partie abandonnee"
        elif self.gagnant == "IA":
            texte_principal = "L'IA gagne !"
        else:
            texte_principal = "Vous gagnez !"
            
        surface_principale = police_grand.render(texte_principal, True, self.BLANC)
        y_message = self.OFFSET_Y - surface_principale.get_height() - 30
        if y_message < 0:
            y_message = 0
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            y_message
        ))

        # Boutons en bas du plateau
        largeur_bouton = 250
        hauteur_bouton = 60
        y_boutons = self.OFFSET_Y + self.TAILLE_CASE * 10 + 40  # Position Y juste sous le plateau
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
        
        # Bouton Rejouer 
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
        
        # Bouton Quitter (rouge)
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

    def reinitialiser_jeu(self):
        """Remet le jeu à l'état initial"""
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
        self.joueur_actuel = self.joueur_humain
        self.game_over = False
        self.gagnant = None
        self.temps_derniere_action = pygame.time.get_ticks()

    def run(self):
        """Boucle principale du jeu"""
        # Redimensionner les pions si ils existent
        if self.pion_blanc and self.pion_noir:
            pion_size = int(self.TAILLE_CASE * 0.8)
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        self.joueur_actuel = self.joueur_humain  # Le joueur humain commence
        self.running = True
        self.temps_derniere_action = pygame.time.get_ticks()
        
        while self.running:
            temps_actuel = pygame.time.get_ticks()
            
            if self.background_image:
                self.ecran.blit(self.background_image, (0, 0))
            else:
                self.ecran.fill(self.BLANC)
            
            self.dessiner_plateau()
            self.afficher_plateau()
            self.afficher_pion_selectionne()
            self.afficher_mouvements_possibles()
            
            if not self.game_over:
                self.afficher_tour()
                self.afficher_info_jeu()
                
                # Si c'est le tour de l'IA et assez de temps s'est écoulé
                if (self.joueur_actuel == self.joueur_ia and 
                    temps_actuel - self.temps_derniere_action >= self.delai_ia):
                    
                    if self.jouer_ia():
                        self.joueur_actuel = self.joueur_humain
                        self.temps_derniere_action = temps_actuel
                    else:
                        # L'IA ne peut pas jouer, fin de partie
                        self.game_over = True
                        self.gagnant = "Joueur"
            else:
                self.afficher_fin_de_jeu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    x, y = event.pos
                    if self.bouton_abandonner and self.bouton_abandonner.collidepoint(x, y):
                        self.game_over = True
                        self.gagnant = "abandon"
                    elif self.joueur_actuel == self.joueur_humain:
                        self.gerer_clic()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                    x, y = event.pos
                    if self.bouton_rejouer.collidepoint(x, y):
                        self.reinitialiser_jeu()
                    elif self.bouton_quitter.collidepoint(x, y):
                        self.running = False
            
            pygame.display.flip()
    