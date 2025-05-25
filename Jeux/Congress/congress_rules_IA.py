import pygame
import sys
import json
import random
import time

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

        # Pions
        try:
            self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
            self.pion_noir = pygame.image.load("assets/pion_noir.png")
        except:
            self.pion_blanc = None
            self.pion_noir = None

        # Plateau de base - Joueur vs IA comme dans Isolation
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
        
        # Configuration IA - EXACTEMENT comme dans Isolation
        self.joueur_humain = 1  # Le joueur humain joue avec les pions blancs
        self.joueur_ia = 2      # L'IA joue avec les pions noirs
        self.delai_ia = 1000    # Délai en millisecondes avant que l'IA joue
        self.temps_derniere_action = 0

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

    def get_pions_joueur(self, joueur):
        """Retourne la liste des positions des pions d'un joueur"""
        pions = []
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == joueur:
                    pions.append((i, j))
        return pions

    def jouer_ia(self):
        """IA qui choisit un mouvement aléatoire parmi tous les mouvements possibles"""
        pions_ia = self.get_pions_joueur(self.joueur_ia)
        
        if not pions_ia:
            return False
        
        # Collecter tous les mouvements possibles pour tous les pions de l'IA
        tous_mouvements = []
        for ligne_pion, col_pion in pions_ia:
            mouvements = self.get_mouvements_possibles(ligne_pion, col_pion)
            for mouvement in mouvements:
                tous_mouvements.append(((ligne_pion, col_pion), mouvement))
        
        if not tous_mouvements:
            return False
        
        # Choisir un mouvement aléatoire
        pion_origine, destination = random.choice(tous_mouvements)
        ligne_dep, col_dep = pion_origine
        ligne_arr, col_arr = destination
        
        print(f"L'IA déplace le pion de ({ligne_dep}, {col_dep}) vers ({ligne_arr}, {col_arr})")
        
        # Effectuer le mouvement
        self.deplacer_pion(pion_origine, destination)
        return True

    def run(self):
        # Redimensionner les pions
        if self.pion_blanc and self.pion_noir:
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (self.TAILLE_CASE, self.TAILLE_CASE))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (self.TAILLE_CASE, self.TAILLE_CASE))
        
        # Variables de jeu - EXACTEMENT comme dans Isolation
        self.joueur_actuel = self.joueur_humain  # Le joueur humain commence
        self.pion_selectionne = None
        self.mouvements_possibles = []  # Liste des mouvements possibles pour le pion sélectionné
        self.running = True
        self.temps_derniere_action = pygame.time.get_ticks()
        
        # Boucle de jeu
        while self.running:
            temps_actuel = pygame.time.get_ticks()
            
            if self.background_image:
                self.ecran.blit(self.background_image, (0, 0))
            else:
                self.ecran.fill(self.BLANC)
            
            # Dessiner le plateau
            self.dessiner_plateau()
            
            # Afficher la prévisualisation des mouvements (seulement pour le joueur humain)
            if self.joueur_actuel == self.joueur_humain:
                self.afficher_preview_mouvements()
            
            # Afficher les pions
            self.afficher_plateau()
            
            # Surligner le pion sélectionné (seulement pour le joueur humain)
            if self.joueur_actuel == self.joueur_humain:
                self.afficher_pion_selectionne()
            
            if not self.game_over:
                self.afficher_tour()
                self.afficher_info_jeu()
                
                # Si c'est le tour de l'IA et assez de temps s'est écoulé
                if (self.joueur_actuel == self.joueur_ia and 
                    temps_actuel - self.temps_derniere_action >= self.delai_ia):
                    
                    if self.jouer_ia():
                        self.joueur_actuel = self.joueur_humain
                        self.temps_derniere_action = temps_actuel
                        
                        # Vérifier si le jeu est terminé après le coup de l'IA
                        if self.verifier_victoire(self.joueur_humain):
                            print("Vous gagnez!")
                            self.game_over = True
                        elif self.verifier_victoire(self.joueur_ia):
                            print("L'IA gagne!")
                            self.game_over = True
                    else:
                        # L'IA ne peut pas jouer, fin de partie
                        self.game_over = True
                        self.gagnant = "humain"
                        print("L'IA ne peut plus jouer, vous gagnez!")
            else:
                self.afficher_fin_de_jeu()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    x, y = event.pos
                    if hasattr(self, 'bouton_abandonner') and self.bouton_abandonner and self.bouton_abandonner.collidepoint(x, y):
                        self.game_over = True
                        self.gagnant = "abandon"
                    elif self.joueur_actuel == self.joueur_humain:  # Ne permettre le clic que si c'est le tour du joueur
                        self.gerer_clic()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                    x, y = event.pos
                    if hasattr(self, 'bouton_rejouer') and self.bouton_rejouer.collidepoint(x, y):
                        self.reinitialiser_jeu()
                    elif hasattr(self, 'bouton_quitter') and self.bouton_quitter.collidepoint(x, y):
                        self.running = False
            
            pygame.display.flip()
        
        pygame.quit()

    def afficher_preview_mouvements(self):
        """Affiche les cases où le pion sélectionné peut se déplacer"""
        if self.pion_selectionne and self.mouvements_possibles:
            # Créer une surface transparente pour les overlays
            overlay = pygame.Surface((self.TAILLE_CASE, self.TAILLE_CASE), pygame.SRCALPHA)
            overlay.fill(self.VERT_PREVIEW)
            
            for ligne, col in self.mouvements_possibles:
                # Dessiner un overlay vert semi-transparent
                self.ecran.blit(overlay, 
                              (self.OFFSET_X + col * self.TAILLE_CASE, 
                               self.OFFSET_Y + ligne * self.TAILLE_CASE))
                
                # Dessiner un contour vert pour plus de visibilité
                pygame.draw.rect(self.ecran, self.VERT, 
                               (self.OFFSET_X + col * self.TAILLE_CASE, 
                                self.OFFSET_Y + ligne * self.TAILLE_CASE, 
                                self.TAILLE_CASE, self.TAILLE_CASE), 3)

    def afficher_pion_selectionne(self):
        """Surligne le pion actuellement sélectionné"""
        if self.pion_selectionne:
            ligne, col = self.pion_selectionne
            # Dessiner un contour orange épais autour du pion sélectionné
            pygame.draw.rect(self.ecran, self.ORANGE, 
                           (self.OFFSET_X + col * self.TAILLE_CASE, 
                            self.OFFSET_Y + ligne * self.TAILLE_CASE, 
                            self.TAILLE_CASE, self.TAILLE_CASE), 5)
    
    def reinitialiser_jeu(self):
        """Réinitialise le jeu pour une nouvelle partie"""
        self.plateau = [[0, 2, 0, 1, 2, 0, 1, 0],
                        [1, 0, 0, 0, 0, 0, 0, 2],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [2, 0, 0, 0, 0, 0, 0, 1],
                        [1, 0, 0, 0, 0, 0, 0, 2],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [2, 0, 0, 0, 0, 0, 0, 1],
                        [0, 1, 0, 2, 1, 0, 2, 0]]
        self.joueur_actuel = self.joueur_humain  # Le joueur humain commence toujours
        self.pion_selectionne = None
        self.mouvements_possibles = []
        self.game_over = False
        self.gagnant = None
        self.temps_derniere_action = pygame.time.get_ticks()

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
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == 1:
                    if self.pion_blanc:
                        self.ecran.blit(self.pion_blanc, 
                                        (self.OFFSET_X + j * self.TAILLE_CASE, 
                                        self.OFFSET_Y + i * self.TAILLE_CASE))
                    else:
                        # Fallback: cercle blanc avec bordure
                        pygame.draw.circle(self.ecran, self.BLANC,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         self.TAILLE_CASE//3)
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         self.TAILLE_CASE//3, 2)
                elif self.plateau[i][j] == 2:
                    if self.pion_noir:
                        self.ecran.blit(self.pion_noir, 
                                        (self.OFFSET_X + j * self.TAILLE_CASE, 
                                        self.OFFSET_Y + i * self.TAILLE_CASE))
                    else:
                        # Fallback: cercle noir
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         self.TAILLE_CASE//3)
    
    def afficher_tour(self):
        """Affiche le tour actuel - EXACTEMENT comme dans Isolation"""
        try:
            police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 35)
        except:
            police = pygame.font.Font(None, 36)
        
        if self.joueur_actuel == self.joueur_humain:
            texte = "Votre tour - Sélectionnez un pion"
            couleur = self.BLANC
        else:
            texte = "L'ordinateur réfléchit..."
            couleur = self.BLANC
        
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))

    def afficher_info_jeu(self):
        """Affiche les informations du jeu et le bouton abandonner"""
        try:
            police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 25)
        except:
            police = pygame.font.Font(None, 25)
        
        # Compter les pions de chaque joueur
        pions_humain = len(self.get_pions_joueur(self.joueur_humain))
        pions_ia = len(self.get_pions_joueur(self.joueur_ia))
        
        texte = f"Vos pions: {pions_humain} | IA: {pions_ia}"
        surface_texte = police.render(texte, True, self.BLANC)
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
        """Affiche l'écran de fin de jeu - EXACTEMENT comme dans Isolation"""
        try:
            police_grand = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
            police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
        except:
            police_grand = pygame.font.Font(None, 40)
            police_bouton = pygame.font.Font(None, 32)
        
        # Déterminer le gagnant
        if self.gagnant == "abandon":
            texte_principal = "Partie abandonnée"
        elif self.verifier_victoire(self.joueur_humain):
            texte_principal = "Vous gagnez !"
        elif self.verifier_victoire(self.joueur_ia):
            texte_principal = "L'ordinateur gagne !"
        else:
            texte_principal = "Match nul !"
            
        surface_principale = police_grand.render(texte_principal, True, self.BLANC)
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            self.HAUTEUR // 2 - 500
        ))

        # Bouton Rejouer
        largeur_bouton = 250
        hauteur_bouton = 60
        self.bouton_rejouer = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton - 20,
            self.HAUTEUR // 2 + 450,
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
            self.HAUTEUR // 2 + 450,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_quitter, border_radius=20)
        texte_quitter = police_bouton.render("Quitter", True, self.BLANC)
        rect_texte_quitter = texte_quitter.get_rect(center=self.bouton_quitter.center)
        self.ecran.blit(texte_quitter, rect_texte_quitter)
    
    def gerer_clic(self):
        """Gère les clics de souris pour le joueur humain"""
        pos = pygame.mouse.get_pos()
        
        # Convertir la position en coordonnées de la grille
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        # Vérifier si le clic est dans les limites du plateau
        if 0 <= ligne < 8 and 0 <= col < 8:
            if self.pion_selectionne is None:
                # Sélection d'un pion du joueur humain
                if self.plateau[ligne][col] == self.joueur_humain:
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
                    self.joueur_actuel = self.joueur_ia  # Passer le tour à l'IA
                    self.temps_derniere_action = pygame.time.get_ticks()
                    
                    # Vérifier si le jeu est terminé après le coup du joueur
                    if self.verifier_victoire(self.joueur_humain):
                        print("Vous gagnez!")
                        self.game_over = True
                    elif self.verifier_victoire(self.joueur_ia):
                        print("L'IA gagne!")
                        self.game_over = True
                else:
                    # Si on clique sur un autre pion du même joueur, le sélectionner
                    if self.plateau[ligne][col] == self.joueur_humain:
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
            return abs(ligne_arr - ligne_dep) <= 1 and abs(col_arr - col_dep) <= 1
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