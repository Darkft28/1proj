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
        pygame.display.set_caption("Katarenga")
        
        # Taille des cases
        self.TAILLE_CASE = int(100 * self.RATIO_X)
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
            sys.exit(1)

        # Bords et coins
        self.BORDURE = "assets/bordure.png"
        self.COINS = "assets/coin.png"
        #pions
        self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
        self.pion_noir = pygame.image.load("assets/pion_noir.png")

        


        #plateau de pions
        self.plateau = [[0, 10, 10, 10, 10, 10, 10, 10, 10, 0],
                        [10, 2, 2, 2, 2, 2, 2, 2, 2, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
                        [10, 1, 1, 1, 1, 1, 1, 1, 1, 10],
                        [0, 10, 10, 10, 10, 10, 10, 10, 10, 0]]
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)

        
    def run(self):
        
        
        # Redimensionner les pions
        self.pion_blanc = pygame.transform.scale(self.pion_blanc, (self.TAILLE_CASE, self.TAILLE_CASE))
        self.pion_noir = pygame.transform.scale(self.pion_noir, (self.TAILLE_CASE, self.TAILLE_CASE))
        
        # Variables de jeu
        self.joueur_actuel = 1  # 1 pour blanc, 2 pour noir
        self.pion_selectionne = None
        self.running = True
        self.transformer_plateau()
        # Boucle de jeu
        while self.running:
            self.ecran.blit(self.background_image, (0, 0))
            
            # Dessiner le plateau
            self.dessiner_plateau()
            self.afficher_plateau()
            
            # Afficher le tour du joueur
            self.afficher_tour()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.gerer_clic()
            
            pygame.display.flip()
        
        pygame.quit()

    def transformer_plateau(self):
        # Charger le fichier JSON contenant les chemins d'images
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
                plateau_8 = json.load(f)
                
                plateau_8.insert(0, [self.BORDURE for _ in range(8)])
                
                plateau_8.append([self.BORDURE for _ in range(8)])

                for row in plateau_8:
                    row.insert(0, self.BORDURE)
                    row.append(self.BORDURE)

                #Coins
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
    def dessiner_plateau(self):
        # Charger le fichier JSON contenant les chemins d'images
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
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
            for i in range(8):
                for j in range(8):
                    couleur = self.BLANC if (i + j) % 2 == 0 else self.NOIR
                    pygame.draw.rect(self.ecran, couleur, 
                                   (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))
    
    def afficher_plateau(self):
        for i in range(1, 9):
            for j in range(1, 9):
                if self.plateau[i][j] == 1:
                    self.ecran.blit(self.pion_blanc, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE))
                elif self.plateau[i][j] == 2:
                    self.ecran.blit(self.pion_noir, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE))
    
    def afficher_tour(self):
        font = pygame.font.Font(None, 36)
        texte = f"Tour du joueur {'Blanc' if self.joueur_actuel == 1 else 'Noir'}"
        couleur = self.BLANC if self.joueur_actuel == 1 else self.NOIR
        surface_texte = font.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 20))
    
    def gerer_clic(self):
        pos = pygame.mouse.get_pos()
        
        # Convertir la position en coordonnées de la grille
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        # Vérifier si le clic est dans les limites du plateau
        if 1 <= ligne < 9 and 1 <= col < 9:
            if self.pion_selectionne is None:
                # Sélection d'un pion
                if self.plateau[ligne][col] == self.joueur_actuel:
                    self.pion_selectionne = (ligne, col)
            else:
                # Déplacement d'un pion
                if self.mouvement_valide(self.pion_selectionne, (ligne, col)):
                    self.deplacer_pion(self.pion_selectionne, (ligne, col))
                    self.pion_selectionne = None
                    self.joueur_actuel = 3 - self.joueur_actuel  # Alternance entre 1 et 2
                    
                    # Vérifier si un joueur a gagné
                    if self.verifier_victoire(1):
                        print("Le joueur Blanc a gagné!")
                        self.running = False
                    elif self.verifier_victoire(2):
                        print("Le joueur Noir a gagné!")
                        self.running = False
                else:
                    # Annuler la sélection si le mouvement est invalide
                    self.pion_selectionne = None
    
    def mouvement_valide(self, depart, arrivee):
        ligne_dep, col_dep = depart
        ligne_arr, col_arr = arrivee
        
        # Vérifier si la case d'arrivée est vide
        if self.joueur_actuel == 1 and self.plateau[ligne_arr][col_arr] == 1:
            return False
        elif self.joueur_actuel == 2 and self.plateau[ligne_arr][col_arr] == 2:
            return False
        else:
            self.plateau[ligne_arr][col_arr] = self.joueur_actuel
        
        try:
            with open("plateaux/plateau_katarenga.json", 'r') as f:
                plateau_images = json.load(f)
            
            # Vérifier si les indices sont dans les limites du plateau
            if ligne_dep >= len(plateau_images) or col_dep >= len(plateau_images[0]):
                return False
                
            image_path = plateau_images[ligne_dep][col_dep]
            
            # Déterminer les mouvements valides selon la couleur
            if "rouge" in image_path.lower():
                return (ligne_arr == ligne_dep or col_arr == col_dep) and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "bleu" in image_path.lower():
                return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1 and not (ligne_arr == ligne_dep and col_arr == col_dep)
            elif "jaune" in image_path.lower():
                return abs(ligne_arr - ligne_dep) == abs(col_arr - col_dep) and ligne_arr != ligne_dep
            elif "vert" in image_path.lower():
                return (abs(ligne_arr - ligne_dep) == 2 and abs(col_arr - col_dep) == 1) or (abs(ligne_arr - ligne_dep) == 1 and abs(col_arr - col_dep) == 2)
            else:
                return True
                
        except Exception as e:
            print(f"Erreur lors de la vérification des règles de mouvement: {e}")
            return False
    
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


# Lancement du jeu
if __name__ == "__main__":
    jeu = Plateau_pion()
    jeu.run()