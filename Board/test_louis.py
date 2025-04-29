import pygame
import sys

class JeuDePlateau:
    # Couleurs
    BLANC = (255, 255, 255)
    NOIR = (40, 40, 40)
    ROUGE = (173, 7, 60)    
    BLEU = (29, 185, 242)     
    JAUNE = (235, 226, 56)    
    VERT = (24, 181, 87)     

    def __init__(self):
        # Initialiser Pygame
        pygame.init()
        
        # Dimensions de l'écran
        self.LARGEUR_ECRAN = 1075 # Largeur augmentée pour le panneau latéral
        self.LARGEUR_JEU = 800     # Largeur originale de la zone de jeu
        self.HAUTEUR_ECRAN = 800
        
        # Dimensions de la grille
        self.TAILLE_GRILLE = 2
        self.TAILLE_TUILE = self.LARGEUR_JEU // self.TAILLE_GRILLE
        
        # Dimensions des petits plateaux
        self.TAILLE_PETIT_PLATEAU = 4
        self.TAILLE_PETITE_TUILE = self.TAILLE_TUILE // self.TAILLE_PETIT_PLATEAU
        
        # Plateau combiné
        self.TAILLE_PLATEAU_COMBINE = self.TAILLE_PETIT_PLATEAU * self.TAILLE_GRILLE  # 8x8
        
        # Constantes du panneau d'édition
        self.POSITION_X_PANNEAU = self.LARGEUR_JEU
        self.LARGEUR_PANNEAU = self.LARGEUR_ECRAN - self.LARGEUR_JEU
        self.TAILLE_APERCU = 150
        self.MARGE_PANNEAU = 20
        
        # Initialiser l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR_ECRAN, self.HAUTEUR_ECRAN))
        pygame.display.set_caption("Placement et Rotation de Plateaux")
        
        # Créer les petits plateaux
        self.petits_plateaux = [
            [[self.ROUGE, self.BLEU, self.JAUNE, self.VERT], 
             [self.BLEU, self.VERT, self.ROUGE, self.JAUNE], 
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU], 
             [self.VERT, self.JAUNE, self.BLEU, self.ROUGE]],
            
            [[self.BLEU, self.VERT, self.ROUGE, self.JAUNE], 
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU], 
             [self.VERT, self.JAUNE, self.BLEU, self.ROUGE], 
             [self.ROUGE, self.BLEU, self.JAUNE, self.VERT]],
            
            [[self.JAUNE, self.ROUGE, self.VERT, self.BLEU], 
             [self.VERT, self.JAUNE, self.BLEU, self.ROUGE], 
             [self.ROUGE, self.BLEU, self.JAUNE, self.VERT], 
             [self.BLEU, self.VERT, self.ROUGE, self.JAUNE]],
            
            [[self.VERT, self.JAUNE, self.BLEU, self.ROUGE], 
             [self.ROUGE, self.BLEU, self.JAUNE, self.VERT], 
             [self.BLEU, self.VERT, self.ROUGE, self.JAUNE], 
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU]]
        ]
        
        # Variables pour le glisser-déposer
        self.plateau_selectionne = None
        self.position_selection = None
        self.rotation_selection = 0
        self.plateaux_places = [None, None, None, None]  # Pour suivre les plateaux placés dans la grille 2x2
        
        # Mode
        self.mode_edition = True  # True: mode édition, False: mode affichage
        self.plateau_combine = None  # Plateau combiné 8x8
        
    def dessiner_grand_plateau(self):
        for ligne in range(self.TAILLE_GRILLE):
            for colonne in range(self.TAILLE_GRILLE):
                rect = pygame.Rect(colonne * self.TAILLE_TUILE, ligne * self.TAILLE_TUILE, 
                                  self.TAILLE_TUILE, self.TAILLE_TUILE)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
    
    def dessiner_petit_plateau(self, plateau, x, y, rotation):
        for ligne in range(self.TAILLE_PETIT_PLATEAU):
            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                # Ajustement pour la rotation
                if rotation == 0:
                    couleur = plateau[ligne][colonne]
                elif rotation == 90:
                    couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - colonne][ligne]
                elif rotation == 180:
                    couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - ligne][self.TAILLE_PETIT_PLATEAU - 1 - colonne]
                elif rotation == 270:
                    couleur = plateau[colonne][self.TAILLE_PETIT_PLATEAU - 1 - ligne]
    
                rect = pygame.Rect(
                    x + colonne * self.TAILLE_PETITE_TUILE, 
                    y + ligne * self.TAILLE_PETITE_TUILE, 
                    self.TAILLE_PETITE_TUILE, 
                    self.TAILLE_PETITE_TUILE
                )
                pygame.draw.rect(self.ecran, couleur, rect)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
    
    def dessiner_panneau_edition(self):
        # Dessiner l'arrière-plan du panneau
        rect_panneau = pygame.Rect(self.POSITION_X_PANNEAU, 0, self.LARGEUR_PANNEAU, self.HAUTEUR_ECRAN)
        pygame.draw.rect(self.ecran, (60, 60, 60), rect_panneau)
        
        # Dessiner le titre
        police = pygame.font.Font(None, 36)
        titre = police.render("Éditeur de Plateau", True, self.BLANC)
        self.ecran.blit(titre, (self.POSITION_X_PANNEAU + self.MARGE_PANNEAU, self.MARGE_PANNEAU))
        
        if self.mode_edition:
            # Dessiner les aperçus des plateaux disponibles
            for idx, plateau in enumerate(self.petits_plateaux):
                if all(self.plateaux_places[i] is None or self.plateaux_places[i][0] != plateau for i in range(4)):
                    position_y = idx * (self.TAILLE_APERCU + self.MARGE_PANNEAU) + 80
                    rect_apercu = pygame.Rect(self.POSITION_X_PANNEAU + self.MARGE_PANNEAU, position_y, 
                                             self.TAILLE_APERCU, self.TAILLE_APERCU)
                    pygame.draw.rect(self.ecran, (80, 80, 80), rect_apercu)
                    pygame.draw.rect(self.ecran, self.BLANC, rect_apercu, 2)
                    
                    # Dessiner une version miniature du plateau
                    mini_tuile = self.TAILLE_APERCU // self.TAILLE_PETIT_PLATEAU
                    for ligne in range(self.TAILLE_PETIT_PLATEAU):
                        for colonne in range(self.TAILLE_PETIT_PLATEAU):
                            couleur = plateau[ligne][colonne]
                            mini_rect = pygame.Rect(
                                self.POSITION_X_PANNEAU + self.MARGE_PANNEAU + colonne * mini_tuile,
                                position_y + ligne * mini_tuile,
                                mini_tuile,
                                mini_tuile
                            )
                            pygame.draw.rect(self.ecran, couleur, mini_rect)
                            pygame.draw.rect(self.ecran, self.BLANC, mini_rect, 1)
            
            # Vérifier si tous les plateaux sont placés
            tous_plateaux_places = all(plateau is not None for plateau in self.plateaux_places)
            
            # Dessiner le bouton accepter seulement si tous les plateaux sont placés
            if tous_plateaux_places:
                bouton_x = self.POSITION_X_PANNEAU + self.MARGE_PANNEAU
                bouton_y = self.HAUTEUR_ECRAN - self.MARGE_PANNEAU - 50
                bouton_largeur = self.LARGEUR_PANNEAU - (2 * self.MARGE_PANNEAU)
                bouton_hauteur = 40
                
                # Dessiner le bouton
                rect_bouton = pygame.Rect(bouton_x, bouton_y, bouton_largeur, bouton_hauteur)
                
                # Changer la couleur au survol
                souris_x, souris_y = pygame.mouse.get_pos()
                if rect_bouton.collidepoint(souris_x, souris_y):
                    couleur_bouton = (100, 200, 100)  # Vert plus clair au survol
                else:
                    couleur_bouton = (50, 150, 50)  # Vert normal
                
                pygame.draw.rect(self.ecran, couleur_bouton, rect_bouton)
                pygame.draw.rect(self.ecran, self.BLANC, rect_bouton, 2)
                
                # Texte du bouton
                police = pygame.font.Font(None, 30)
                texte = police.render("Accepter", True, self.BLANC)
                rect_texte = texte.get_rect(center=rect_bouton.center)
                self.ecran.blit(texte, rect_texte)
                
                return rect_bouton  # Retourner le rectangle pour la détection de clic
            
        return None
    
    def gerer_souris_appui(self, pos):
        souris_x, souris_y = pos
        
        # Vérifier si le clic est dans le panneau d'édition
        if self.POSITION_X_PANNEAU <= souris_x <= self.LARGEUR_ECRAN:
            # Vérifier le clic sur le bouton
            rect_bouton = self.dessiner_panneau_edition()
            if rect_bouton and rect_bouton.collidepoint(souris_x, souris_y):
                if self.mode_edition:
                    # Vérifier si tous les plateaux sont placés
                    if all(plateau is not None for plateau in self.plateaux_places):
                        self.creer_plateau_combine()
                        self.mode_edition = False
                else:
                    # Bouton de réinitialisation cliqué
                    self.mode_edition = True
                    self.plateau_combine = None
                    self.plateaux_places = [None, None, None, None]
                    self.plateau_selectionne = None
                    self.position_selection = None
                    self.rotation_selection = 0
                return
            
            # Gérer la sélection de plateau uniquement en mode édition
            if self.mode_edition:
                idx = (souris_y - 80) // (self.TAILLE_APERCU + self.MARGE_PANNEAU)
                if 0 <= idx < len(self.petits_plateaux):
                    if all(self.plateaux_places[i] is None or self.plateaux_places[i][0] != self.petits_plateaux[idx] for i in range(4)):
                        self.plateau_selectionne = idx
                        self.position_selection = (self.POSITION_X_PANNEAU + self.MARGE_PANNEAU, 
                                                80 + idx * (self.TAILLE_APERCU + self.MARGE_PANNEAU))
        
        # Vérifier si un plateau placé est cliqué (seulement en mode édition)
        elif self.mode_edition:
            for idx, info_plateau in enumerate(self.plateaux_places):
                if info_plateau is not None:
                    plateau, x, y, rotation = info_plateau
                    if x <= souris_x < x + self.TAILLE_TUILE and y <= souris_y < y + self.TAILLE_TUILE:
                        self.plateau_selectionne = self.petits_plateaux.index(plateau)
                        self.position_selection = (souris_x, souris_y)
                        self.plateaux_places[idx] = None
                        break
    
    def gerer_souris_relache(self, pos):
        # Gérer uniquement en mode édition
        if not self.mode_edition:
            return
            
        if self.plateau_selectionne is not None:
            souris_x, souris_y = pos
            
            if souris_x < self.LARGEUR_JEU:  # Placer uniquement dans la zone de jeu
                grille_x = souris_x // self.TAILLE_TUILE
                grille_y = souris_y // self.TAILLE_TUILE
                
                if 0 <= grille_x < self.TAILLE_GRILLE and 0 <= grille_y < self.TAILLE_GRILLE:
                    indice_cible = grille_y * self.TAILLE_GRILLE + grille_x
                    
                    info_plateau_existant = self.plateaux_places[indice_cible]
                    self.plateaux_places[indice_cible] = (
                        self.petits_plateaux[self.plateau_selectionne],
                        grille_x * self.TAILLE_TUILE,
                        grille_y * self.TAILLE_TUILE,
                        self.rotation_selection
                    )
                    
                    if info_plateau_existant is not None:
                        ancien_plateau, _, _, ancienne_rotation = info_plateau_existant
                        self.plateau_selectionne = self.petits_plateaux.index(ancien_plateau)
                        self.rotation_selection = ancienne_rotation
                        self.position_selection = (souris_x, souris_y)
                    else:
                        self.plateau_selectionne = None
                        self.position_selection = None
    
    def gerer_touche_appui(self, touche):
        # Gérer uniquement en mode édition
        if not self.mode_edition:
            return
            
        if self.plateau_selectionne is not None:
            if touche == pygame.K_r:  # Faire tourner le plateau
                self.rotation_selection = (self.rotation_selection + 90) % 360
    
    def gerer_souris_mouvement(self, pos):
        # Gérer uniquement en mode édition
        if not self.mode_edition:
            return
            
        if self.plateau_selectionne is not None and self.position_selection is not None:
            self.position_selection = pos
            
    def creer_plateau_combine(self):
        """Créer un plateau 8x8 combiné à partir des quatre plateaux 4x4 placés"""
        # Initialiser le plateau 8x8
        self.plateau_combine = [[None for _ in range(self.TAILLE_PLATEAU_COMBINE)] for _ in range(self.TAILLE_PLATEAU_COMBINE)]
        
        # Traiter chaque plateau placé
        for idx, info_plateau in enumerate(self.plateaux_places):
            if info_plateau is not None:
                plateau, _, _, rotation = info_plateau
                
                # Calculer la position dans la grande grille
                grille_x = idx % self.TAILLE_GRILLE
                grille_y = idx // self.TAILLE_GRILLE
                
                # Remplir le plateau combiné avec les couleurs de ce petit plateau
                for petite_ligne in range(self.TAILLE_PETIT_PLATEAU):
                    for petite_colonne in range(self.TAILLE_PETIT_PLATEAU):
                        # Obtenir la couleur en fonction de la rotation
                        if rotation == 0:
                            couleur = plateau[petite_ligne][petite_colonne]
                        elif rotation == 90:
                            couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - petite_colonne][petite_ligne]
                        elif rotation == 180:
                            couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - petite_ligne][self.TAILLE_PETIT_PLATEAU - 1 - petite_colonne]
                        elif rotation == 270:
                            couleur = plateau[petite_colonne][self.TAILLE_PETIT_PLATEAU - 1 - petite_ligne]
                            
                        # Calculer la position dans le plateau combiné
                        ligne_combinee = (grille_y * self.TAILLE_PETIT_PLATEAU) + petite_ligne
                        colonne_combinee = (grille_x * self.TAILLE_PETIT_PLATEAU) + petite_colonne
                        
                        # Définir la couleur
                        self.plateau_combine[ligne_combinee][colonne_combinee] = couleur
    
    def dessiner(self):
        self.ecran.fill(self.NOIR)
        
        if self.mode_edition:
            # Dessiner la zone de jeu
            self.dessiner_grand_plateau()
            
            # Dessiner les petits plateaux placés
            for idx, info_plateau in enumerate(self.plateaux_places):
                if info_plateau is not None:
                    plateau, x, y, rotation = info_plateau
                    self.dessiner_petit_plateau(plateau, x, y, rotation)
            
            # Dessiner le plateau actuellement déplacé
            if self.plateau_selectionne is not None and self.position_selection is not None:
                souris_x, souris_y = self.position_selection
                self.dessiner_petit_plateau(self.petits_plateaux[self.plateau_selectionne], 
                                  souris_x - self.TAILLE_PETITE_TUILE * 2,
                                  souris_y - self.TAILLE_PETITE_TUILE * 2,
                                  self.rotation_selection)
        else:
            # Dessiner le plateau combiné
            if self.plateau_combine:
                self.dessiner_plateau_combine()
        
        # Dessiner le panneau d'édition (toujours)
        self.dessiner_panneau_edition()
        
        pygame.display.flip()
        
    def dessiner_plateau_combine(self):
        # Dessiner le plateau combiné 8x8
        taille_cellule = self.LARGEUR_JEU // self.TAILLE_PLATEAU_COMBINE
        
        for ligne in range(self.TAILLE_PLATEAU_COMBINE):
            for colonne in range(self.TAILLE_PLATEAU_COMBINE):
                couleur = self.plateau_combine[ligne][colonne]
                
                if couleur:
                    rect = pygame.Rect(
                        colonne * taille_cellule, 
                        ligne * taille_cellule, 
                        taille_cellule, 
                        taille_cellule
                    )
                    pygame.draw.rect(self.ecran, couleur, rect)
                    pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
    
    def executer(self):
        en_cours = True
        horloge = pygame.time.Clock()
        
        while en_cours:
            try:
                evenements = pygame.event.get()
                for evenement in evenements:
                    if evenement.type == pygame.QUIT:
                        en_cours = False
                    elif evenement.type == pygame.KEYDOWN:
                        if evenement.key == pygame.K_ESCAPE:  # Quitter avec la touche Échap
                            en_cours = False
                        else:
                            self.gerer_touche_appui(evenement.key)
                    elif evenement.type == pygame.MOUSEBUTTONDOWN:
                        self.gerer_souris_appui(evenement.pos)
                    elif evenement.type == pygame.MOUSEBUTTONUP:
                        self.gerer_souris_relache(evenement.pos)
                    elif evenement.type == pygame.MOUSEMOTION:
                        self.gerer_souris_mouvement(evenement.pos)
            
            except Exception as e:
                print(f"Exception non gérée: {e}")
                pygame.event.clear()
            
            self.dessiner()
            horloge.tick(60)  # Limiter à 60 FPS
        
        pygame.quit()
        sys.exit()

# Point d'entrée principal
if __name__ == "__main__":
    jeu = JeuDePlateau()
    jeu.executer()