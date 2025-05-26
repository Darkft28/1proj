import pygame
import sys
import json

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
        pygame.display.set_caption("Congress")
        
        # Taille des cases
        self.TAILLE_CASE = int(120 * self.RATIO_X)
        self.OFFSET_X = (self.LARGEUR - 8 * self.TAILLE_CASE) // 2
        self.OFFSET_Y = (self.HAUTEUR - 8 * self.TAILLE_CASE) // 2
        
        # Fond d'écran
        self.background_image = pygame.image.load("assets/menu-claire/fond-menu-principal.png")
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

    def get_couleur_case(self, ligne, col):
        """Récupère la couleur d'une case depuis le fichier JSON"""
        try:
            with open("plateaux/plateau_17.json", 'r') as f:
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
        pion_size = int(self.TAILLE_CASE * 0.8)  # 0.6 = 60% de la case, ajuste si besoin
        offset = (self.TAILLE_CASE - pion_size) // 2
        self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
        self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        # Variables de jeu
        self.joueur_actuel = 1  # 1 pour blanc, 2 pour noir
        self.pion_selectionne = None
        self.mouvements_possibles = []  # Liste des mouvements possibles pour le pion sélectionné
        self.running = True
        
        # Boucle de jeu
        while self.running:
            self.ecran.blit(self.background_image, (0, 0))
            self.dessiner_plateau()
            self.afficher_preview_mouvements()
            self.afficher_plateau()
            self.afficher_pion_selectionne()
            self.afficher_tour()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.gerer_clic()
            
            pygame.display.flip()
        
        pygame.quit()

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
            with open("plateaux/plateau_17.json", 'r') as f:
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
        joueur_nom = "Joueur 1" if self.joueur_actuel == 1 else "Joueur 2"
        texte = f"Tour du joueur {joueur_nom}"
        couleur = self.NOIR if self.joueur_actuel == 2 else self.BLANC
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))
    
    def gerer_clic(self):
        pos = pygame.mouse.get_pos()
        
        # Convertir la position en coordonnées de la grille
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        # Vérifier si le clic est dans les limites du plateau
        if 0 <= ligne < 8 and 0 <= col < 8:
            if self.pion_selectionne is None:
                # Sélection d'un pion
                if self.plateau[ligne][col] == self.joueur_actuel:
                    self.pion_selectionne = (ligne, col)
                    # Calculer les mouvements possibles pour ce pion
                    self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
                    print(f"Pion sélectionné en ({ligne}, {col}). {len(self.mouvements_possibles)} mouvements possibles.")
            else:
                # Déplacement d'un pion
                if self.mouvement_valide(self.pion_selectionne, (ligne, col)):
                    self.deplacer_pion(self.pion_selectionne, (ligne, col))
                    self.pion_selectionne = None
                    self.mouvements_possibles = []  # Effacer la prévisualisation
                    self.joueur_actuel = 3 - self.joueur_actuel  # Alternance entre 1 et 2
                    
                    # Vérifier si un joueur a gagné
                    if self.verifier_victoire(1):
                        print("Le joueur Blanc a gagné!")
                        self.running = False
                    elif self.verifier_victoire(2):
                        print("Le joueur Noir a gagné!")
                        self.running = False
                else:
                    # Si on clique sur un autre pion du même joueur, le sélectionner
                    if self.plateau[ligne][col] == self.joueur_actuel:
                        self.pion_selectionne = (ligne, col)
                        self.mouvements_possibles = self.get_mouvements_possibles(ligne, col)
                        print(f"Nouveau pion sélectionné en ({ligne}, {col}). {len(self.mouvements_possibles)} mouvements possibles.")
                    else:
                        # Annuler la sélection si le mouvement est invalide
                        self.pion_selectionne = None
                        self.mouvements_possibles = []
    
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
        if couleur_case == "rouge":  # Tour - mouvement ligne/colonne jusqu'à obstacle ou case rouge
            return self.mouvement_tour(ligne_dep, col_dep, ligne_arr, col_arr)
        elif couleur_case == "bleu":  # Roi - 8 cases adjacentes
            return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_arr) <= 1
        elif couleur_case == "jaune":  # Fou - mouvement diagonal jusqu'à obstacle ou case jaune
            return self.mouvement_fou(ligne_dep, col_dep, ligne_arr, col_arr)
        elif couleur_case == "vert":  # Cavalier - mouvement en L
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


# Lancement du jeu
if __name__ == "__main__":
    jeu = Plateau_pion()
    jeu.run()