import pygame
import sys
import os
import json

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
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        
        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440
        
        # Dimensions de l'écran adaptées
        self.LARGEUR_JEU = int(self.LARGEUR * 0.7)  # 70% de l'écran pour le jeu
        self.HAUTEUR_JEU = int(self.HAUTEUR * 0.5)
        self.LARGEUR_PANNEAU = int(self.LARGEUR * 0.3)  # 30% pour le panneau
        self.LARGEUR_ECRAN = self.LARGEUR
        self.HAUTEUR_ECRAN = self.HAUTEUR
        
        # Dimensions de la grille
        self.TAILLE_GRILLE = 2
        self.TAILLE_TUILE = self.HAUTEUR // self.TAILLE_GRILLE
        
        # Dimensions des petits plateaux
        self.TAILLE_PETIT_PLATEAU = 4
        self.TAILLE_PETITE_TUILE = self.TAILLE_TUILE // self.TAILLE_PETIT_PLATEAU
        
        # Plateau combiné
        self.TAILLE_PLATEAU_COMBINE = self.TAILLE_PETIT_PLATEAU * self.TAILLE_GRILLE  # 8x8
        
        # Constantes du panneau d'édition
        self.POSITION_X_PANNEAU = self.LARGEUR_JEU
        self.LARGEUR_PANNEAU = self.LARGEUR_ECRAN - self.LARGEUR_JEU
        self.TAILLE_APERCU = int(150 * min(self.RATIO_X, self.RATIO_Y))
        self.MARGE_PANNEAU = int(20 * min(self.RATIO_X, self.RATIO_Y))
        
        # Initialiser l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR_ECRAN, self.HAUTEUR_ECRAN), pygame.FULLSCREEN)
        pygame.display.set_caption("Placement et Rotation de Plateaux")
        
        self.images = {}
        try:
            self.images["assets/image_rouge.png"] = pygame.image.load("assets/image_rouge.png").convert_alpha()
            self.images["assets/image_bleue.png"] = pygame.image.load("assets/image_bleue.png").convert_alpha()
            self.images["assets/image_jaune.png"] = pygame.image.load("assets/image_jaune.png").convert_alpha()
            self.images["assets/image_verte.png"] = pygame.image.load("assets/image_verte.png").convert_alpha()
        except pygame.error as e:
            print(f"Erreur lors du chargement des images: {e}")
            pygame.quit()
            sys.exit()
        
        # Créer les petits plateaux
        self.petits_plateaux = self.charger_plateaux_sauvegardes()
        
        # Créer les petits plateaux
        self.petits_plateaux = self.charger_plateaux_sauvegardes()
        if not self.petits_plateaux:  # Si aucun plateau n'est trouvé
            print("Aucun plateau trouvé dans le dossier 'plateaux'")
            pygame.quit()
            sys.exit()
        
        # Variables pour le glisser-déposer
        self.plateau_selectionne = None
        self.position_selection = None
        self.rotation_selection = 0
        self.plateaux_places = [None, None, None, None]
        
        # Mode
        self.mode_edition = True
        self.plateau_combine = None
        self.cacher_aperçus = False
        
    def dessiner_grand_plateau(self):
        for ligne in range(self.TAILLE_GRILLE):
            for colonne in range(self.TAILLE_GRILLE):
                rect = pygame.Rect(
                    int(colonne * self.TAILLE_TUILE), 
                    int(ligne * self.TAILLE_TUILE),
                    int(self.TAILLE_TUILE), 
                    int(self.TAILLE_TUILE)
                )
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
    
    def dessiner_panneau_edition(self):
        if self.cacher_aperçus is not True:
            # Dessiner l'arrière-plan du panneau
            rect_panneau = pygame.Rect(self.POSITION_X_PANNEAU, 0, self.LARGEUR_PANNEAU, self.HAUTEUR_ECRAN)
            pygame.draw.rect(self.ecran, (60, 60, 60), rect_panneau)
            
            # Dessiner le titre
            police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
            titre = police.render("Éditeur de Plateau", True, self.BLANC)
            self.ecran.blit(titre, (self.POSITION_X_PANNEAU + self.MARGE_PANNEAU, self.MARGE_PANNEAU))
            
            if self.mode_edition:
                # Dessiner les aperçus des plateaux disponibles
                for idx, plateau in enumerate(self.petits_plateaux):
                    if all(self.plateaux_places[i] is None or self.plateaux_places[i][0] != plateau for i in range(4)):
                        position_y = idx * (self.TAILLE_APERCU + self.MARGE_PANNEAU) + int(80 * self.RATIO_Y)
                        rect_apercu = pygame.Rect(
                            self.POSITION_X_PANNEAU + self.MARGE_PANNEAU,
                            position_y,
                            self.TAILLE_APERCU,
                            self.TAILLE_APERCU
                        )
                        pygame.draw.rect(self.ecran, (80, 80, 80), rect_apercu)
                        pygame.draw.rect(self.ecran, self.BLANC, rect_apercu, 2)
                        
                        # Dessiner une version miniature du plateau
                        mini_tuile = self.TAILLE_APERCU // self.TAILLE_PETIT_PLATEAU
                        for ligne in range(self.TAILLE_PETIT_PLATEAU):
                            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                                chemin_image = plateau[ligne][colonne]
                                mini_rect = pygame.Rect(
                                    int(self.POSITION_X_PANNEAU + self.MARGE_PANNEAU + colonne * mini_tuile),
                                    int(position_y + ligne * mini_tuile),
                                    int(mini_tuile),
                                    int(mini_tuile)
                                )
                                if chemin_image and chemin_image in self.images:
                                    image = pygame.transform.scale(self.images[chemin_image], 
                                                                (int(mini_tuile), int(mini_tuile)))
                                    self.ecran.blit(image, mini_rect)
                                else:
                                    pygame.draw.rect(self.ecran, self.NOIR, mini_rect)
                                pygame.draw.rect(self.ecran, self.BLANC, mini_rect, 1)

    def dessiner_plateau_combine(self):
        taille_cellule = self.LARGEUR_JEU // self.TAILLE_PLATEAU_COMBINE
        
        for ligne in range(self.TAILLE_PLATEAU_COMBINE):
            for colonne in range(self.TAILLE_PLATEAU_COMBINE):
                chemin_image = self.plateau_combine[ligne][colonne]
                
                if chemin_image:
                    rect = pygame.Rect(
                        int(colonne * taille_cellule),
                        int(ligne * taille_cellule),
                        int(taille_cellule),
                        int(taille_cellule)
                    )
                    
                    if chemin_image in self.images:
                        image = pygame.transform.scale(self.images[chemin_image], 
                                                    (int(taille_cellule), int(taille_cellule)))
                        self.ecran.blit(image, rect)
                    else:
                        pygame.draw.rect(self.ecran, self.NOIR, rect)
                    
                    pygame.draw.rect(self.ecran, self.BLANC, rect, 1)

    def dessiner(self):
        self.ecran.fill(self.NOIR)
        
        if self.mode_edition:
            self.dessiner_grand_plateau()
            
            for idx, info_plateau in enumerate(self.plateaux_places):
                if info_plateau is not None:
                    plateau, x, y, rotation = info_plateau
                    self.dessiner_petit_plateau(plateau, x, y, rotation)
            
            if self.plateau_selectionne is not None and self.position_selection is not None:
                souris_x, souris_y = self.position_selection
                self.dessiner_petit_plateau(
                    self.petits_plateaux[self.plateau_selectionne],
                    int(souris_x - self.TAILLE_PETITE_TUILE * 2),
                    int(souris_y - self.TAILLE_PETITE_TUILE * 2),
                    self.rotation_selection
                )
        else:
            if self.plateau_combine:
                self.dessiner_plateau_combine()
        
        self.dessiner_panneau_edition()
        pygame.display.flip()

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
                        self.cacher_aperçus = True
                        
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
                    
    def charger_plateaux_sauvegardes(self):
        """Charge les plateaux depuis les fichiers JSON dans le dossier plateaux"""
        plateaux = []
        
        # Vérifier si le dossier existe
        if not os.path.exists("plateaux"):
            print("Le dossier 'plateaux' n'existe pas")
            return []
        
        # Charger chaque fichier JSON
        for fichier in os.listdir("plateaux"):
            if fichier.endswith('.json'):
                try:
                    with open(os.path.join("plateaux", fichier), 'r') as f:
                        plateau = json.load(f)
                        plateaux.append(plateau)  # Garder les chemins d'images directement
                except Exception as e:
                    print(f"Erreur lors du chargement de {fichier}: {e}")
        
        if not plateaux:
            # Créer un plateau par défaut avec des chemins d'images null
            plateau_defaut = [[None for _ in range(self.TAILLE_PETIT_PLATEAU)] 
                            for _ in range(self.TAILLE_PETIT_PLATEAU)]
            plateaux.append(plateau_defaut)
        
        return plateaux

    def dessiner_petit_plateau(self, plateau, x, y, rotation):
        for ligne in range(self.TAILLE_PETIT_PLATEAU):
            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                # Ajustement pour la rotation
                if rotation == 0:
                    chemin_image = plateau[ligne][colonne]
                elif rotation == 90:
                    chemin_image = plateau[self.TAILLE_PETIT_PLATEAU - 1 - colonne][ligne]
                elif rotation == 180:
                    chemin_image = plateau[self.TAILLE_PETIT_PLATEAU - 1 - ligne][self.TAILLE_PETIT_PLATEAU - 1 - colonne]
                elif rotation == 270:
                    chemin_image = plateau[colonne][self.TAILLE_PETIT_PLATEAU - 1 - ligne]

                rect = pygame.Rect(
                    int(x + colonne * self.TAILLE_PETITE_TUILE),
                    int(y + ligne * self.TAILLE_PETITE_TUILE),
                    int(self.TAILLE_PETITE_TUILE),
                    int(self.TAILLE_PETITE_TUILE)
                )
                
                # Dessiner le fond
                pygame.draw.rect(self.ecran, self.NOIR, rect)
                
                # Dessiner l'image si disponible
                if chemin_image and chemin_image in self.images:
                    image = pygame.transform.scale(self.images[chemin_image], 
                                                (int(self.TAILLE_PETITE_TUILE),
                                                int(self.TAILLE_PETITE_TUILE)))
                    self.ecran.blit(image, rect)
                
                # Dessiner la bordure
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