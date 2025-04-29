import pygame
import sys

class EditeurPlateau:
    def __init__(self):
        pygame.init()
        
        # Dimensions de l'écran
        self.LARGEUR_ECRAN = 1000
        self.LARGEUR_JEU = 800
        self.HAUTEUR_ECRAN = 800
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        
        # Dimensions de la grille
        self.TAILLE_GRILLE = 2
        self.TAILLE_CASE = self.LARGEUR_JEU // self.TAILLE_GRILLE
        
        # Dimensions des petits plateaux
        self.TAILLE_PETIT_PLATEAU = 4
        self.TAILLE_PETITE_CASE = self.TAILLE_CASE // self.TAILLE_PETIT_PLATEAU
        
        # Constantes du panneau d'édition
        self.POS_X_PANNEAU = self.LARGEUR_JEU
        self.LARGEUR_PANNEAU = self.LARGEUR_ECRAN - self.LARGEUR_JEU
        self.TAILLE_APERCU = 150
        self.MARGE_PANNEAU = 20
        
        # Initialisation de l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR_ECRAN, self.HAUTEUR_ECRAN))
        pygame.display.set_caption("Éditeur de Plateaux")
        
        # Création des petits plateaux
        self.petits_plateaux = [
            # Plateau 1 - Configuration standard
            [[self.ROUGE, self.BLEU, self.JAUNE, self.VERT], 
             [self.BLEU, self.VERT, self.ROUGE, self.JAUNE],
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU], 
             [self.VERT, self.JAUNE, self.BLEU, self.ROUGE]],
            
            # Plateau 2 - Configuration en spirale
            [[self.ROUGE, self.ROUGE, self.ROUGE, self.BLEU],
             [self.VERT, self.JAUNE, self.BLEU, self.BLEU],
             [self.VERT, self.ROUGE, self.JAUNE, self.BLEU],
             [self.VERT, self.VERT, self.VERT, self.JAUNE]],
            
            # Plateau 3 - Configuration en damier
            [[self.ROUGE, self.BLEU, self.ROUGE, self.BLEU],
             [self.BLEU, self.ROUGE, self.BLEU, self.ROUGE],
             [self.ROUGE, self.BLEU, self.ROUGE, self.BLEU],
             [self.BLEU, self.ROUGE, self.BLEU, self.ROUGE]],
            
            # Plateau 4 - Configuration diagonale
            [[self.ROUGE, self.VERT, self.BLEU, self.JAUNE],
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU],
             [self.BLEU, self.JAUNE, self.ROUGE, self.VERT],
             [self.VERT, self.BLEU, self.JAUNE, self.ROUGE]]
        ]
        
        # Variables de glisser-déposer
        self.plateau_selectionne = None
        self.position_selection = None
        self.rotation_selection = 0
        self.plateaux_places = [None, None, None, None]

    def dessiner_grand_plateau(self):
        for ligne in range(self.TAILLE_GRILLE):
            for colonne in range(self.TAILLE_GRILLE):
                rect = pygame.Rect(colonne * self.TAILLE_CASE, ligne * self.TAILLE_CASE, 
                                 self.TAILLE_CASE, self.TAILLE_CASE)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)

    def dessiner_petit_plateau(self, plateau, x, y, rotation):
        for ligne in range(self.TAILLE_PETIT_PLATEAU):
            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                if rotation == 0:
                    couleur = plateau[ligne][colonne]
                elif rotation == 90:
                    couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - colonne][ligne]
                elif rotation == 180:
                    couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - ligne][self.TAILLE_PETIT_PLATEAU - 1 - colonne]
                elif rotation == 270:
                    couleur = plateau[colonne][self.TAILLE_PETIT_PLATEAU - 1 - ligne]

                rect = pygame.Rect(x + colonne * self.TAILLE_PETITE_CASE, 
                                 y + ligne * self.TAILLE_PETITE_CASE,
                                 self.TAILLE_PETITE_CASE, self.TAILLE_PETITE_CASE)
                pygame.draw.rect(self.ecran, couleur, rect)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)

    def dessiner_panneau_edition(self):
        # Fond du panneau
        rect_panneau = pygame.Rect(self.POS_X_PANNEAU, 0, self.LARGEUR_PANNEAU, self.HAUTEUR_ECRAN)
        pygame.draw.rect(self.ecran, (60, 60, 60), rect_panneau)
        
        # Titre
        police = pygame.font.Font(None, 36)
        titre = police.render("Éditeur de Plateaux", True, self.BLANC)
        self.ecran.blit(titre, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, self.MARGE_PANNEAU))
        
        # Aperçu des plateaux disponibles
        for idx, plateau in enumerate(self.petits_plateaux):
            if all(self.plateaux_places[i] is None or self.plateaux_places[i][0] != plateau 
                  for i in range(4)):
                self._dessiner_apercu_plateau(idx, plateau)

    def _dessiner_apercu_plateau(self, idx, plateau):
        y_pos = idx * (self.TAILLE_APERCU + self.MARGE_PANNEAU) + 80
        rect_apercu = pygame.Rect(self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos, 
                                self.TAILLE_APERCU, self.TAILLE_APERCU)
        pygame.draw.rect(self.ecran, (80, 80, 80), rect_apercu)
        pygame.draw.rect(self.ecran, self.BLANC, rect_apercu, 2)
        
        taille_mini = self.TAILLE_APERCU // self.TAILLE_PETIT_PLATEAU
        for ligne in range(self.TAILLE_PETIT_PLATEAU):
            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                couleur = plateau[ligne][colonne]
                rect_mini = pygame.Rect(
                    self.POS_X_PANNEAU + self.MARGE_PANNEAU + colonne * taille_mini,
                    y_pos + ligne * taille_mini,
                    taille_mini, taille_mini
                )
                pygame.draw.rect(self.ecran, couleur, rect_mini)
                pygame.draw.rect(self.ecran, self.BLANC, rect_mini, 1)

    def executer(self):
        en_cours = True
        horloge = pygame.time.Clock()

        while en_cours:
            self.ecran.fill(self.NOIR)
            self.dessiner_grand_plateau()
            self.dessiner_panneau_edition()
            self._gerer_plateaux_places()
            
            try:
                en_cours = self._gerer_evenements()
            except Exception as e:
                print(f"Erreur non gérée: {e}")
                pygame.event.clear()

            self._dessiner_plateau_selectionne()
            pygame.display.flip()
            horloge.tick(60)  # Limite à 60 FPS

        pygame.quit()
        sys.exit()

    def _gerer_plateaux_places(self):
        for idx, info_plateau in enumerate(self.plateaux_places):
            if info_plateau is not None:
                plateau, x, y, rotation = info_plateau
                self.dessiner_petit_plateau(plateau, x, y, rotation)

    def _gerer_evenements(self):
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                return False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:  # Quitter avec Échap
                    return False
            
            self._gerer_clic_souris(evenement)
            self._gerer_relache_souris(evenement)
            self._gerer_rotation(evenement)
            self._gerer_mouvement_souris(evenement)
        
        return True

    def _gerer_clic_souris(self, evenement):
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            souris_x, souris_y = evenement.pos
            
            # Vérifier si le clic est dans le panneau d'édition
            if self.POS_X_PANNEAU <= souris_x <= self.LARGEUR_ECRAN:
                idx = (souris_y - 80) // (self.TAILLE_APERCU + self.MARGE_PANNEAU)
                if 0 <= idx < len(self.petits_plateaux):
                    if all(self.plateaux_places[i] is None or 
                          self.plateaux_places[i][0] != self.petits_plateaux[idx] 
                          for i in range(4)):
                        self.plateau_selectionne = idx
                        self.position_selection = evenement.pos
            
            # Vérifier si un plateau placé est cliqué
            else:
                for idx, info_plateau in enumerate(self.plateaux_places):
                    if info_plateau is not None:
                        plateau, x, y, rotation = info_plateau
                        if (x <= souris_x < x + self.TAILLE_CASE and 
                            y <= souris_y < y + self.TAILLE_CASE):
                            self.plateau_selectionne = self.petits_plateaux.index(plateau)
                            self.position_selection = evenement.pos
                            self.rotation_selection = rotation
                            self.plateaux_places[idx] = None
                            break

    def _gerer_relache_souris(self, evenement):
        if (evenement.type == pygame.MOUSEBUTTONUP and 
            self.plateau_selectionne is not None):
            souris_x, souris_y = evenement.pos
            
            if souris_x < self.LARGEUR_JEU:  # Placement uniquement dans la zone de jeu
                grille_x = souris_x // self.TAILLE_CASE
                grille_y = souris_y // self.TAILLE_CASE
                
                if 0 <= grille_x < self.TAILLE_GRILLE and 0 <= grille_y < self.TAILLE_GRILLE:
                    index_cible = grille_y * self.TAILLE_GRILLE + grille_x
                    
                    plateau_existant = self.plateaux_places[index_cible]
                    self.plateaux_places[index_cible] = (
                        self.petits_plateaux[self.plateau_selectionne],
                        grille_x * self.TAILLE_CASE,
                        grille_y * self.TAILLE_CASE,
                        self.rotation_selection
                    )
                    
                    if plateau_existant is not None:
                        ancien_plateau, _, _, ancienne_rotation = plateau_existant
                        self.plateau_selectionne = self.petits_plateaux.index(ancien_plateau)
                        self.rotation_selection = ancienne_rotation
                        self.position_selection = evenement.pos
                    else:
                        self.plateau_selectionne = None
                        self.position_selection = None

    def _gerer_rotation(self, evenement):
        if (evenement.type == pygame.KEYDOWN and 
            self.plateau_selectionne is not None):
            if evenement.key == pygame.K_r:  # Rotation avec la touche R
                self.rotation_selection = (self.rotation_selection + 90) % 360

    def _gerer_mouvement_souris(self, evenement):
        if (evenement.type == pygame.MOUSEMOTION and 
            self.plateau_selectionne is not None and 
            self.position_selection is not None):
            self.position_selection = evenement.pos

    def _dessiner_plateau_selectionne(self):
        if self.plateau_selectionne is not None and self.position_selection is not None:
            souris_x, souris_y = self.position_selection
            self.dessiner_petit_plateau(
                self.petits_plateaux[self.plateau_selectionne],
                souris_x - self.TAILLE_PETITE_CASE * 2,
                souris_y - self.TAILLE_PETITE_CASE * 2,
                self.rotation_selection
            )

if __name__ == "__main__":
    editeur = EditeurPlateau()
    editeur.executer()