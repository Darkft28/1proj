import random
import pygame
import sys
import json
from menu.config import get_theme

class Plateau_pion:
    def __init__(self):
        pygame.init()
        self.pion_selectionne = None
        self.mouvements_possibles = []
        
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
        pygame.display.set_caption("Congress")
        
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
        self.ORANGE = (255, 165, 0)  # Pour la prévisualisation
        self.VERT_PREVIEW = (0, 255, 0, 128)  # Vert semi-transparent pour les mouvements possibles

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
            sys.exit(1)

        # Pions
        self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
        self.pion_noir = pygame.image.load("assets/pion_noir.png")

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

        # Joueurs
        self.joueur_humain = 1
        self.joueur_ia = 2
        self.delai_ia = 700  # ms
        self.temps_derniere_action = 0

        # État du jeu
        self.game_over = False
        self.gagnant = None        
        self.bouton_abandonner = None
        self.bouton_rejouer = None
        self.bouton_quitter = None

    def get_couleur_case(self, ligne, col):
        """Récupère la couleur d'une case depuis le fichier JSON"""
        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_images = json.load(f)
            
            # Vérifier si les indices sont dans les limites du plateau
            if ligne >= len(plateau_images) or col >= len(plateau_images[0]):
                return None
                
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
            return None

    def get_mouvements_possibles(self, ligne, col):
        """Retourne la liste des mouvements possibles pour un pion à la position donnée"""
        mouvements = []
        
        for i in range(8):
            for j in range(8):
                if self.mouvement_valide((ligne, col), (i, j)):
                    mouvements.append((i, j))
        
        return mouvements

    def run(self):
        # Redimensionner les pions
        pion_size = int(self.TAILLE_CASE * 0.8)
        offset = (self.TAILLE_CASE - pion_size) // 2
        self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
        self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        self.joueur_actuel = self.joueur_humain
        self.running = True
        self.temps_derniere_action = pygame.time.get_ticks()
        
        while self.running:
            temps_actuel = pygame.time.get_ticks()
            self.ecran.blit(self.background_image, (0, 0))
            self.dessiner_plateau()
            self.afficher_preview_mouvements()
            self.afficher_plateau()
            self.afficher_pion_selectionne()
            
            if not self.game_over:
                self.afficher_tour()
                self.afficher_bouton_abandonner()
            else:
                self.afficher_fin_de_jeu()

            # Si c'est le tour de l'IA et délai écoulé, l'IA joue
            if (self.joueur_actuel == self.joueur_ia and 
                temps_actuel - self.temps_derniere_action >= self.delai_ia):
                self.jouer_ia()
                self.temps_derniere_action = temps_actuel

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if not self.game_over:
                        if self.bouton_abandonner and self.bouton_abandonner.collidepoint(x, y):
                            self.game_over = True
                            self.gagnant = "Joueur 1"  # ou "Joueur 2" selon le cas
                        else:
                            self.gerer_clic()
                    else:
                        if self.bouton_rejouer and self.bouton_rejouer.collidepoint(x, y):
                            self.reinitialiser_jeu()
                        elif self.bouton_quitter and self.bouton_quitter.collidepoint(x, y):
                            self.running = False
            pygame.display.flip()
        return           # <-- AJOUTE cette ligne

    def afficher_preview_mouvements(self):
        """Affiche des cercles noirs pour les mouvements possibles"""
        if self.pion_selectionne and self.mouvements_possibles:
            rayon = self.TAILLE_CASE // 4  # La moitié du rayon du pion
            for ligne, col in self.mouvements_possibles:
                centre_x = self.OFFSET_X + col * self.TAILLE_CASE + self.TAILLE_CASE // 2
                centre_y = self.OFFSET_Y + ligne * self.TAILLE_CASE + self.TAILLE_CASE // 2
                pygame.draw.circle(self.ecran, self.NOIR, (centre_x, centre_y), rayon)

    def afficher_pion_selectionne(self):
        """Affiche un cercle autour du pion sélectionné"""
        if self.pion_selectionne:
            ligne, col = self.pion_selectionne
            centre_x = self.OFFSET_X + col * self.TAILLE_CASE + self.TAILLE_CASE // 2
            centre_y = self.OFFSET_Y + ligne * self.TAILLE_CASE + self.TAILLE_CASE // 2
            rayon = int(self.TAILLE_CASE * 0.42)
            pygame.draw.circle(self.ecran, self.VERT, (centre_x, centre_y), rayon, 5)
    def dessiner_plateau(self):
        # Charger le fichier JSON contenant les chemins d'images
        try:
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_images = json.load(f)
            
            # Si le plateau JSON n'est pas de taille 8x8, on l'adapte
            if len(plateau_images) < 8 or len(plateau_images[0]) < 8:
                # Répéter les motifs pour atteindre 8x8
                plateau_complet = []
                for i in range(8):
                    ligne = []
                    for j in range(8):
                        ligne.append(plateau_images[i % len(plateau_images)][j % len(plateau_images[0])])
                    plateau_complet.append(ligne)
                plateau_images = plateau_complet

            # Dessiner les images du plateau
            for i in range(8):
                for j in range(8):
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
            for i in range(8):
                for j in range(8):
                    couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
                    pygame.draw.rect(self.ecran, couleur, 
                                   (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))
    
    def afficher_plateau(self):
        pion_size = int(self.TAILLE_CASE * 0.8)
        offset = (self.TAILLE_CASE - pion_size) // 2
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == 1:
                    self.ecran.blit(self.pion_blanc, 
                        (self.OFFSET_X + j * self.TAILLE_CASE + offset, 
                        self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                elif self.plateau[i][j] == 2:
                    self.ecran.blit(self.pion_noir, 
                        (self.OFFSET_X + j * self.TAILLE_CASE + offset, 
                        self.OFFSET_Y + i * self.TAILLE_CASE + offset))
    
    def afficher_tour(self):
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 35)
        if self.joueur_actuel == self.joueur_humain:
            texte = "Votre tour - Placez votre pion"
            couleur = self.NOIR
        else:
            texte = "L'ordinateur reflechit..."
            couleur = self.BLANC
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))
    
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
        if couleur_case == "rouge":
            return self.mouvement_tour(ligne_dep, col_dep, ligne_arr, col_arr)
        elif couleur_case == "bleu":  # Roi - 8 cases adjacentes
            # Correction ici : remplacer col_arr par col_dep dans la deuxième condition
            return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1
        elif couleur_case == "jaune":
            return self.mouvement_fou(ligne_dep, col_dep, ligne_arr, col_arr)
        elif couleur_case == "vert":
            return ((abs(ligne_arr - ligne_dep) == 2 and abs(col_arr - col_dep) == 1) or 
                    (abs(ligne_arr - ligne_dep) == 1 and abs(col_arr - col_dep) == 2))
        else:
            return True

    def mouvement_tour(self, ligne_dep, col_dep, ligne_arr, col_arr):
        """Vérifie si un mouvement de tour est valide (ligne/colonne jusqu'à obstacle ou case rouge)"""
        # Vérifier que c'est bien un mouvement en ligne ou en colonne
        if ligne_dep != ligne_arr and col_dep != col_arr:
            return False
        
        # Calculer la direction
        if ligne_dep == ligne_arr:  # Mouvement horizontal
            direction = 1 if col_arr > col_dep else -1
            col_actuel = col_dep + direction
            
            while col_actuel != col_arr:
                # Vérifier s'il y a un obstacle (pion)
                if self.plateau[ligne_dep][col_actuel] != 0:
                    return False
                
                # Vérifier si on rencontre une case rouge (arrêt obligatoire)
                couleur = self.get_couleur_case(ligne_dep, col_actuel)
                if couleur == "rouge":
                    return False
                
                col_actuel += direction
                
        else:  # Mouvement vertical
            direction = 1 if ligne_arr > ligne_dep else -1
            ligne_actuel = ligne_dep + direction
            
            while ligne_actuel != ligne_arr:
                # Vérifier s'il y a un obstacle (pion)
                if self.plateau[ligne_actuel][col_dep] != 0:
                    return False
                
                # Vérifier si on rencontre une case rouge (arrêt obligatoire)
                couleur = self.get_couleur_case(ligne_actuel, col_dep)
                if couleur == "rouge":
                    return False
                
                ligne_actuel += direction
        
        return True

    def mouvement_fou(self, ligne_dep, col_dep, ligne_arr, col_arr):
        """Vérifie si un mouvement de fou est valide (diagonal jusqu'à obstacle ou case jaune)"""
        # Vérifier que c'est bien un mouvement diagonal
        if abs(ligne_arr - ligne_dep) != abs(col_arr - col_dep):
            return False
        
        # Calculer les directions
        dir_ligne = 1 if ligne_arr > ligne_dep else -1
        dir_col = 1 if col_arr > col_dep else -1
        
        ligne_actuel = ligne_dep + dir_ligne
        col_actuel = col_dep + dir_col
        
        while ligne_actuel != ligne_arr or col_actuel != col_arr:
            # Vérifier s'il y a un obstacle (pion)
            if self.plateau[ligne_actuel][col_actuel] != 0:
                return False
            
            # Vérifier si on rencontre une case jaune (arrêt obligatoire)
            couleur = self.get_couleur_case(ligne_actuel, col_actuel)
            if couleur == "jaune":
                return False
            
            ligne_actuel += dir_ligne
            col_actuel += dir_col
        
        return True
    
    def deplacer_pion(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        # Déplacer le pion
        self.plateau[ligne_arr][col_arr] = self.plateau[ligne_dep][col_dep]
        self.plateau[ligne_dep][col_dep] = 0
    
    def verifier_victoire(self, joueur):
        # Trouver tous les pions du joueur
        positions = []
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == joueur:
                    positions.append((i, j))
        
        # Si aucun pion, pas de victoire
        if not positions:
            return False
        
        # Vérifier si tous les pions sont connectés
        visites = set()
        pile = [positions[0]]
        
        while pile:
            pos = pile.pop()
            visites.add(pos)
            
            # Vérifier les voisins orthogonaux
            i, j = pos
            for ni, nj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:
                if 0 <= ni < 8 and 0 <= nj < 8 and self.plateau[ni][nj] == joueur and (ni, nj) not in visites:
                    pile.append((ni, nj))
        
        # Victoire si tous les pions sont visités
        return len(visites) == len(positions)

    def jouer_ia(self):
        # IA random : choisit un pion, puis un mouvement possible au hasard
        pions_ia = []
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == self.joueur_ia:
                    pions_ia.append((i, j))
        random.shuffle(pions_ia)
        for pion in pions_ia:
            mouvements = self.get_mouvements_possibles(*pion)
            if mouvements:
                depart = pion
                arrivee = random.choice(mouvements)
                self.deplacer_pion(depart, arrivee)
                # Vérifier victoire
                if self.verifier_victoire(self.joueur_ia):
                    self.game_over = True
                    self.gagnant = "Joueur 2"
                self.joueur_actuel = self.joueur_humain
                return

    def gerer_clic(self):
        pos = pygame.mouse.get_pos()
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE

        if 0 <= ligne < 8 and 0 <= col < 8:
            if self.pion_selectionne is None:
                if self.plateau[ligne][col] == self.joueur_actuel:
                    self.pion_selectionne = (ligne, col)
                    self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
            else:
                if self.mouvement_valide(self.pion_selectionne, (ligne, col)):
                    self.deplacer_pion(self.pion_selectionne, (ligne, col))
                    self.pion_selectionne = None
                    self.mouvements_possibles = []
                    self.joueur_actuel = self.joueur_ia
                    self.temps_derniere_action = pygame.time.get_ticks()
                    # Vérifier victoire
                    if self.verifier_victoire(self.joueur_humain):
                        self.game_over = True
                        self.gagnant = "Joueur 1"
                else:
                    if self.plateau[ligne][col] == self.joueur_actuel:
                        self.pion_selectionne = (ligne, col)
                        self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
                    else:
                        self.pion_selectionne = None
                        self.mouvements_possibles = []

    def afficher_bouton_abandonner(self):
        largeur_bouton = 220
        hauteur_bouton = 50
        x = self.LARGEUR - largeur_bouton - 30
        y = self.HAUTEUR - hauteur_bouton - 30
        self.bouton_abandonner = pygame.Rect(x, y, largeur_bouton, hauteur_bouton)
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_abandonner, border_radius=20)
        texte_abandonner = police.render("Abandonner", True, self.BLANC)
        rect_texte = texte_abandonner.get_rect(center=self.bouton_abandonner.center)
        self.ecran.blit(texte_abandonner, rect_texte)

    def afficher_fin_de_jeu(self):
        police_grand = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        
        # Message de victoire au-dessus du plateau
        if self.gagnant == "abandon":
            texte_principal = "Partie abandonnée"
        else:
            texte_principal = f"{self.gagnant} gagne !"
        
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
        y_boutons = self.OFFSET_Y + (8 * self.TAILLE_CASE) + 40  # Position Y juste sous le plateau
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
        
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
        
    def reinitialiser_jeu(self):
        # Plateau de départ (positions d'origine)
        self.plateau = [
            [0, 2, 0, 1, 2, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 2],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 2],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 2, 1, 0, 2, 0]
        ]
        self.pion_selectionne = None
        self.mouvements_possibles = []
        self.joueur_actuel = self.joueur_humain
        self.game_over = False
        self.gagnant = None
        self.temps_derniere_action = pygame.time.get_ticks()

if __name__ == "__main__":
    jeu = Plateau_pion()
    jeu.run()
