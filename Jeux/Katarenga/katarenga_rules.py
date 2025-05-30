import pygame
import sys
import json
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
        
        # Variables de jeu
        self.joueur_actuel = 1  # 1 pour blanc, 2 pour noir
        self.pion_selectionne = None
        self.mouvements_possibles = []
        self.running = True

    def run(self):
        # Redimensionner les pions
        if self.pion_blanc and self.pion_noir:
            pion_size = int(self.TAILLE_CASE * 0.8)
            offset = (self.TAILLE_CASE - pion_size) // 2
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        # Boucle de jeu
        while self.running:
            self.ecran.blit(self.background_image, (0, 0))
            
            # Dessiner le plateau
            self.dessiner_plateau()
            self.afficher_plateau()
            
            if not self.game_over:
                self.afficher_tour()
                self.afficher_bouton_abandonner()
            else:
                self.afficher_fin_de_jeu()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if not self.game_over:
                        if hasattr(self, 'bouton_abandonner') and self.bouton_abandonner.collidepoint(x, y):
                            self.game_over = True
                            self.gagnant = "abandon"
                        else:
                            self.gerer_clic()
                    else:
                        if hasattr(self, 'bouton_rejouer') and self.bouton_rejouer.collidepoint(x, y):
                            self.reinitialiser_jeu()
                        elif hasattr(self, 'bouton_quitter') and self.bouton_quitter.collidepoint(x, y):
                            self.running = False
            
            pygame.display.flip()
        
        pygame.quit()

    def dessiner_plateau(self):
        # Charger le fichier JSON contenant les chemins d'images
        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_images = json.load(f)
            
            # Vérifier que le plateau est 10x10
            if len(plateau_images) != 10 or len(plateau_images[0]) != 10:
                print(f"Erreur: Le plateau devrait être 10x10, mais il est {len(plateau_images)}x{len(plateau_images[0])}")
                # Fallback: dessiner un damier basique 10x10
                for i in range(10):
                    for j in range(10):
                        couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
                        pygame.draw.rect(self.ecran, couleur, 
                                       (self.OFFSET_X + j * self.TAILLE_CASE, 
                                        self.OFFSET_Y + i * self.TAILLE_CASE, 
                                        self.TAILLE_CASE, self.TAILLE_CASE))
                return

            # Dessiner les images du plateau 10x10
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
            # Fallback: dessiner un damier basique 10x10
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
        font = pygame.font.Font(self.font_path, int(36 * self.RATIO_Y)) if self.font_path else pygame.font.Font(None, int(36 * self.RATIO_Y))
        texte = f"Tour du joueur {'Blanc' if self.joueur_actuel == 1 else 'Noir'}"
        couleur = self.BLANC if self.joueur_actuel == 1 else self.NOIR
        surface_texte = font.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, int(20 * self.RATIO_Y)))

    def afficher_bouton_abandonner(self):
        # Bouton Abandonner
        police_bouton = pygame.font.Font(self.font_path, int(24 * self.RATIO_Y)) if self.font_path else pygame.font.Font(None, int(24 * self.RATIO_Y))
        self.bouton_abandonner = pygame.Rect(
            int(20 * self.RATIO_X),
            int(20 * self.RATIO_Y),
            int(150 * self.RATIO_X),
            int(50 * self.RATIO_Y)
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_abandonner, border_radius=20)
        texte_abandonner = police_bouton.render("Abandonner", True, self.BLANC)
        rect_texte_abandonner = texte_abandonner.get_rect(center=self.bouton_abandonner.center)
        self.ecran.blit(texte_abandonner, rect_texte_abandonner)

    def afficher_fin_de_jeu(self):
        police_grand = pygame.font.Font(self.font_path, int(40 * self.RATIO_Y)) if self.font_path else pygame.font.Font(None, int(40 * self.RATIO_Y))
        
        # Texte principal
        if self.gagnant == "abandon":
            texte_principal = "Partie abandonnée"
        else:
            texte_principal = f"{self.gagnant} gagne !"
        
        surface_principale = police_grand.render(texte_principal, True, self.BLANC)
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            self.HAUTEUR // 2 - int(200 * self.RATIO_Y)
        ))

        # Boutons
        largeur_bouton = int(250 * self.RATIO_X)
        hauteur_bouton = int(60 * self.RATIO_Y)
        police_bouton = pygame.font.Font(self.font_path, int(32 * self.RATIO_Y)) if self.font_path else pygame.font.Font(None, int(32 * self.RATIO_Y))
        
        # Bouton Rejouer
        self.bouton_rejouer = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton - int(20 * self.RATIO_X),
            self.HAUTEUR // 2 - hauteur_bouton // 2,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.VERT, self.bouton_rejouer, border_radius=20)
        texte_rejouer = police_bouton.render("Rejouer", True, self.BLANC)
        rect_texte_rejouer = texte_rejouer.get_rect(center=self.bouton_rejouer.center)
        self.ecran.blit(texte_rejouer, rect_texte_rejouer)

        # Bouton Quitter
        self.bouton_quitter = pygame.Rect(
            self.LARGEUR // 2 + int(20 * self.RATIO_X),
            self.HAUTEUR // 2 - hauteur_bouton // 2,
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
        # TODO: Implémenter la logique pour obtenir tous les mouvements possibles
        return []

    def mouvement_valide(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
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
            
            # Si le pion est sur la ligne adverse, il peut aller dans un camp adverse
            # sans contraintes de mouvement (déplacement libre)
            if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3) or \
               (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4):
                print(f"Le joueur {self.joueur_actuel} entre dans un camp adverse!")
                return True
        
        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_images = json.load(f)
            
            # Vérifier si les indices sont dans les limites du plateau 10x10
            if ligne_dep >= len(plateau_images) or col_dep >= len(plateau_images[0]):
                return False
                
            image_path = plateau_images[ligne_dep][col_dep]
            
            if "rouge" in image_path.lower():
                # Mouvement en ligne droite (horizontal ou vertical)
                return (ligne_arr == ligne_dep or col_arr == col_dep) and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "bleu" in image_path.lower():
                # Mouvement de roi (une case dans toutes les directions)
                return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1 and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "jaune" in image_path.lower():
                # Mouvement en diagonale
                return abs(ligne_arr - ligne_dep) == abs(col_arr - col_dep) and ligne_arr != ligne_dep
            elif "vert" in image_path.lower():
                # Mouvement de cavalier
                return (abs(ligne_arr - ligne_dep) == 2 and abs(col_arr - col_dep) == 1) or \
                       (abs(ligne_arr - ligne_dep) == 1 and abs(col_arr - col_dep) == 2)
            else:
                # Mouvement libre pour les autres cases
                return True
                
        except Exception as e:
            print(f"Erreur lors de la vérification des règles de mouvement: {e}")
            return False

    def deplacer_pion(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        # Vérifier si le pion va dans un camp adverse
        pion_entre_dans_camp = False
        if (self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 3) or \
           (self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 4):
            pion_entre_dans_camp = True
            print(f"Le pion du joueur {self.joueur_actuel} entre définitivement dans le camp adverse!")
        
        # Capturer le pion
        if self.plateau[ligne_arr][col_arr] in [1, 2] and not pion_entre_dans_camp:
            pion_capture = self.plateau[ligne_arr][col_arr]
            print(f"Pion {pion_capture} capturé!")
        
        # Déplacer le pion
        if pion_entre_dans_camp:
            self.plateau[ligne_dep][col_dep] = 0
            print(f"Le pion est maintenant dans le camp et ne peut plus revenir en jeu.")
        else:
            # Déplacement normal
            self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
            self.plateau[ligne_dep][col_dep] = 0

    def verifier_victoire(self, joueur):
        # Trouver tous les pions du joueur
        positions = []
        for i in range(10):
            for j in range(10):
                if self.plateau[i][j] == joueur:
                    positions.append((i, j))
        
        # Si aucun pion, pas de victoire
        if not positions:
            return False
        
        # TODO: Implémenter la logique de victoire complète
        return False

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

# Lancement du jeu
if __name__ == "__main__":
    jeu = Plateau_pion()
    jeu.run()