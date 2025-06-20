# filepath: c:\Users\robin\Desktop\supinfo\1proj\1proj\Board\board_complet.py
import pygame
import json
import os
import sys
from menu.config import get_theme

class SelecteurPlateau:
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
        
        theme = get_theme()
        if theme == "Sombre":
            self.background_image = pygame.image.load("assets/menu/menu-sombre.png")
        else:
            self.background_image = pygame.image.load("assets/menu/menu-claire.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        
        # Variables de pagination
        self.page_courante = 0
        self.nombre_pages = 0
        
        # Variables de mise en page
        self.total_largeur = 0
        self.total_hauteur = 0
        self.debut_x = 0
        self.debut_y = 0
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        
        # Configuration de l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Sélection du Plateau")
        
        # Chargement des images
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
          # Liste des plateaux
        self.plateaux_sauvegardes = []
        self.boutons_plateaux = []
        
        # Variables pour les transformations de plateaux (AVANT charger_liste_plateaux)
        self.plateaux_transformations = {}  # Dictionnaire pour stocker les transformations de chaque plateau
        self.boutons_rotation_gauche = []
        self.boutons_rotation_droite = []
        self.boutons_miroir = []
        
        # Charger la liste initiale
        self.charger_liste_plateaux()
        
        # Ajout des variables pour la sélection multiple
        self.plateaux_selectionnes = []
        self.NOMBRE_PLATEAUX_REQUIS = 4
        self.COULEUR_SELECTION = (24, 181, 87)  # Vert

        # Ajouter les variables pour le drag and drop
        self.dragging = False
        self.dragged_plateau = None
        self.drag_start_pos = None
        self.dropped_plateaux = [[None, None], [None, None]]  # Grille 2x2 pour stocker les plateaux placés

    def charger_liste_plateaux(self):
        self.plateaux_sauvegardes = []
        self.boutons_plateaux = []
        
        if not os.path.exists("plateaux"):
            print("Aucun plateau trouvé!")
            return
            
        # Charger tous les fichiers JSON
        self.plateaux_sauvegardes = [f for f in os.listdir("plateaux") if f.endswith('.json')]
        
        # Calculer le nombre total de pages
        self.nombre_pages = (len(self.plateaux_sauvegardes) + 7) // 8

        # Initialiser les transformations pour chaque plateau
        for plateau in self.plateaux_sauvegardes:
            if plateau not in self.plateaux_transformations:
                self.plateaux_transformations[plateau] = {
                    'rotation': 0,  # 0, 90, 180, 270
                    'mirroir': False
                }

    def rotationner_plateau(self, plateau_data, sens_horaire=True):
        """Rotation d'un plateau de 90° dans le sens horaire ou anti-horaire"""
        taille = len(plateau_data)
        plateau_rotation = [[None for _ in range(taille)] for _ in range(taille)]
        
        for i in range(taille):
            for j in range(taille):
                if sens_horaire:
                    nouveau_i = j
                    nouveau_j = taille - 1 - i
                else:
                    nouveau_i = taille - 1 - j
                    nouveau_j = i
                plateau_rotation[nouveau_i][nouveau_j] = plateau_data[i][j]
        
        return plateau_rotation

    def miroir_plateau(self, plateau_data):
        """Effet miroir horizontal sur un plateau"""
        taille = len(plateau_data)
        plateau_miroir = [[None for _ in range(taille)] for _ in range(taille)]
        
        for i in range(taille):
            for j in range(taille):
                plateau_miroir[i][taille - 1 - j] = plateau_data[i][j]
        
        return plateau_miroir

    def appliquer_transformations(self, plateau_data, nom_plateau):
        """Applique toutes les transformations stockées pour un plateau"""
        plateau_transforme = [row[:] for row in plateau_data]  # Copie profonde
        
        if nom_plateau in self.plateaux_transformations:
            transformations = self.plateaux_transformations[nom_plateau]
            
            # Appliquer les rotations
            rotation = transformations['rotation']
            for _ in range(rotation // 90):
                plateau_transforme = self.rotationner_plateau(plateau_transforme, sens_horaire=True)
            
            # Appliquer le miroir
            if transformations['mirroir']:
                plateau_transforme = self.miroir_plateau(plateau_transforme)
        
        return plateau_transforme

    def dessiner_ecran_selection(self):
        self.ecran.blit(self.background_image, (0, 0))
        
        # Titre
        police = pygame.font.Font(None, int(48 * min(self.RATIO_X, self.RATIO_Y)))
        titre = police.render("Sélectionnez un plateau", True, self.BLANC)
        titre_rect = titre.get_rect(centerx=self.LARGEUR // 2, y=int(30 * self.RATIO_Y))
        self.ecran.blit(titre, titre_rect)          # Dimensions des miniatures
        taille_miniature = int(250 * min(self.RATIO_X, self.RATIO_Y))  # Réduit davantage
        espace = int(120 * min(self.RATIO_X, self.RATIO_Y))  # Beaucoup plus d'espace
        
        # Calcul pour centrer la grille 4x2
        self.total_largeur = (taille_miniature * 4) + (espace * 3)
        self.total_hauteur = (taille_miniature * 2) + espace
        
        self.debut_x = (self.LARGEUR - self.total_largeur) // 2
        self.debut_y = (self.HAUTEUR - self.total_hauteur) // 2
        
        # Afficher les miniatures
        debut_index = self.page_courante * 8
        self.boutons_plateaux = []
        self.boutons_rotation_gauche = []
        self.boutons_rotation_droite = []
        self.boutons_miroir = []
        
        for i in range(min(8, len(self.plateaux_sauvegardes) - debut_index)):
            ligne = i // 4
            colonne = i % 4
            x = self.debut_x + colonne * (taille_miniature + espace)
            y = self.debut_y + ligne * (taille_miniature + espace)
            
            rect = pygame.Rect(x, y, taille_miniature, taille_miniature)
            self.boutons_plateaux.append(rect)
            
            # Fond gris pour tous les plateaux
            pygame.draw.rect(self.ecran, (60, 60, 60), rect)
            
            # Afficher la prévisualisation avec transformations
            try:
                with open(f"plateaux/{self.plateaux_sauvegardes[debut_index + i]}", 'r') as f:
                    plateau_data = json.load(f)
                    # Appliquer les transformations
                    plateau_transforme = self.appliquer_transformations(plateau_data, self.plateaux_sauvegardes[debut_index + i])
                    taille_tuile = taille_miniature // 4
                    
                    for ligne_p in range(4):
                        for col_p in range(4):
                            chemin_image = plateau_transforme[ligne_p][col_p]
                            tuile_rect = pygame.Rect(
                                x + (col_p * taille_tuile),
                                y + (ligne_p * taille_tuile),
                                taille_tuile,
                                taille_tuile
                            )
                            
                            if chemin_image:
                                couleur = (self.ROUGE if "rouge" in chemin_image else
                                         self.BLEU if "bleue" in chemin_image else
                                         self.JAUNE if "jaune" in chemin_image else
                                         self.VERT)
                                image = pygame.transform.scale(
                                    self.images[couleur],
                                    (taille_tuile, taille_tuile)
                                )
                                self.ecran.blit(image, tuile_rect)
                            pygame.draw.rect(self.ecran, self.BLANC, tuile_rect, 1)
            except Exception as e:
                print(f"Erreur lors du chargement de la miniature {debut_index + i}: {e}")

            # Dessiner la bordure de sélection APRÈS les tuiles
            if self.plateaux_sauvegardes[debut_index + i] in self.plateaux_selectionnes:
                pygame.draw.rect(self.ecran, self.COULEUR_SELECTION, rect, 8)  # Bordure verte épaisse
            else:
                pygame.draw.rect(self.ecran, self.BLANC, rect, 2)  # Bordure blanche fine            # Ajouter les boutons de rotation (flèches) à côté de chaque miniature
            taille_bouton = int(40 * min(self.RATIO_X, self.RATIO_Y))  # Plus grand pour compenser
            
            # Flèche rotation gauche
            fleche_gauche_rect = pygame.Rect(
                x - taille_bouton - 15,  # Encore plus d'espace
                y + taille_miniature // 2 - taille_bouton // 2,
                taille_bouton,
                taille_bouton
            )
            pygame.draw.rect(self.ecran, self.BLEU, fleche_gauche_rect)
            pygame.draw.rect(self.ecran, self.BLANC, fleche_gauche_rect, 2)
            self.boutons_rotation_gauche.append(fleche_gauche_rect)
            
            # Texte flèche gauche
            police_bouton = pygame.font.Font(None, int(32 * min(self.RATIO_X, self.RATIO_Y)))  # Police encore plus grande
            texte_gauche = police_bouton.render("<", True, self.BLANC)
            rect_texte_gauche = texte_gauche.get_rect(center=fleche_gauche_rect.center)
            self.ecran.blit(texte_gauche, rect_texte_gauche)
            
            # Flèche rotation droite
            fleche_droite_rect = pygame.Rect(
                x + taille_miniature + 15,  # Encore plus d'espace
                y + taille_miniature // 2 - taille_bouton // 2,
                taille_bouton,
                taille_bouton
            )
            pygame.draw.rect(self.ecran, self.BLEU, fleche_droite_rect)
            pygame.draw.rect(self.ecran, self.BLANC, fleche_droite_rect, 2)
            self.boutons_rotation_droite.append(fleche_droite_rect)
            
            # Texte flèche droite
            texte_droite = police_bouton.render(">", True, self.BLANC)
            rect_texte_droite = texte_droite.get_rect(center=fleche_droite_rect.center)
            self.ecran.blit(texte_droite, rect_texte_droite)
            
            # Bouton miroir en dessous de la miniature
            bouton_miroir_rect = pygame.Rect(
                x + taille_miniature // 4,
                y + taille_miniature + 15,  # Encore plus d'espace en bas
                taille_miniature // 2,
                int(35 * min(self.RATIO_X, self.RATIO_Y))  # Plus grand
            )
            pygame.draw.rect(self.ecran, self.ROUGE, bouton_miroir_rect)  # Changé en rouge
            pygame.draw.rect(self.ecran, self.BLANC, bouton_miroir_rect, 2)
            self.boutons_miroir.append(bouton_miroir_rect)
            
            # Texte bouton miroir
            police_miroir = pygame.font.Font(None, int(20 * min(self.RATIO_X, self.RATIO_Y)))  # Police plus grande
            texte_miroir = police_miroir.render("Miroir", True, self.BLANC)
            rect_texte_miroir = texte_miroir.get_rect(center=bouton_miroir_rect.center)
            self.ecran.blit(texte_miroir, rect_texte_miroir)

        # Boutons de navigation
        if self.nombre_pages > 1:
            if self.page_courante > 0:
                prec_rect = pygame.Rect(
                    int(self.debut_x - 100 * self.RATIO_X),
                    int(self.debut_y + self.total_hauteur//2),
                    int(50 * self.RATIO_X),
                    int(50 * self.RATIO_Y)
                )
                pygame.draw.rect(self.ecran, self.BLEU, prec_rect)
                police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
                texte = police.render("<", True, self.BLANC)
                rect_texte = texte.get_rect(center=prec_rect.center)
                self.ecran.blit(texte, rect_texte)
            
            if self.page_courante < self.nombre_pages - 1:
                suiv_rect = pygame.Rect(
                    int(self.debut_x + self.total_largeur + 50 * self.RATIO_X),
                    int(self.debut_y + self.total_hauteur//2),
                    int(50 * self.RATIO_X),
                    int(50 * self.RATIO_Y)
                )
                pygame.draw.rect(self.ecran, self.BLEU, suiv_rect)
                texte = police.render(">", True, self.BLANC)
                rect_texte = texte.get_rect(center=suiv_rect.center)
                self.ecran.blit(texte, rect_texte)

        # Bouton retour
        retour_rect = pygame.Rect(
            int(50 * self.RATIO_X),
            int(50 * self.RATIO_Y),
            int(200 * self.RATIO_X),
            int(50 * self.RATIO_Y)
        )
        
        pygame.draw.rect(self.ecran, self.ROUGE, retour_rect)
        pygame.draw.rect(self.ecran, self.BLANC, retour_rect, 2)
        
        police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
        texte = police.render("Retour", True, self.BLANC)
        rect_texte = texte.get_rect(center=retour_rect.center)
        self.ecran.blit(texte, rect_texte)
        
        # Bouton suivant (uniquement si 4 plateaux sont sélectionnés)
        if len(self.plateaux_selectionnes) == self.NOMBRE_PLATEAUX_REQUIS:
            suivant_rect = pygame.Rect(
                int(self.LARGEUR - 250 * self.RATIO_X),
                int(50 * self.RATIO_Y),
                int(200 * self.RATIO_X),
                int(50 * self.RATIO_Y)
            )
            pygame.draw.rect(self.ecran, self.VERT, suivant_rect)
            pygame.draw.rect(self.ecran, self.BLANC, suivant_rect, 2)
            
            police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
            texte = police.render("Suivant", True, self.BLANC)
            rect_texte = texte.get_rect(center=suivant_rect.center)
            self.ecran.blit(texte, rect_texte)
            
            return retour_rect, suivant_rect
        
        return retour_rect, None

    def afficher_ecran_final(self, plateaux_selectionnes):
        self.ecran.blit(self.background_image, (0, 0))
        
        # Dimensions du plateau central (2x2) - Augmenté de 75%
        taille_plateau_central = int(1050 * min(self.RATIO_X, self.RATIO_Y))  # 600 * 1.75
        taille_quadrant = taille_plateau_central // 2
        
        # Position du plateau central (au milieu)
        debut_x_central = (self.LARGEUR - taille_plateau_central) // 2
        debut_y_central = (self.HAUTEUR - taille_plateau_central) // 2
        
        # Dessiner la grille centrale 2x2
        for ligne in range(2):
            for col in range(2):
                rect = pygame.Rect(
                    debut_x_central + col * taille_quadrant,
                    debut_y_central + ligne * taille_quadrant,
                    taille_quadrant,
                    taille_quadrant
                )
                # Dessiner le fond
                pygame.draw.rect(self.ecran, (60, 60, 60), rect)
                # Dessiner la bordure
                pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
                
                # Afficher le plateau s'il a été déposé à cet emplacement
                if self.dropped_plateaux[ligne][col]:
                    try:
                        self.dessiner_plateau_miniature(
                            self.dropped_plateaux[ligne][col],
                            rect.x, rect.y,
                            taille_quadrant
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'affichage du plateau déposé: {e}")
        
        # Dimensions des plateaux latéraux
        taille_plateau_lateral = int(250 * min(self.RATIO_X, self.RATIO_Y))
        
        # Afficher les plateaux sélectionnés non déposés
        plateaux_non_deposes = [p for p in plateaux_selectionnes if not any(p in row for row in self.dropped_plateaux)]
        for i, plateau in enumerate(plateaux_non_deposes):
            if i < 2:  # Gauche
                x = int(50 * self.RATIO_X)
                y = int((self.HAUTEUR // 4) + (i * taille_plateau_lateral * 1.2))
            else:  # Droite
                x = self.LARGEUR - int(50 * self.RATIO_X) - taille_plateau_lateral
                y = int((self.HAUTEUR // 4) + ((i-2) * taille_plateau_lateral * 1.2))
                
            rect = pygame.Rect(x, y, taille_plateau_lateral, taille_plateau_lateral)
            if plateau != self.dragged_plateau:
                try:
                    self.dessiner_plateau_miniature(plateau, x, y, taille_plateau_lateral)
                except Exception as e:
                    print(f"Erreur lors de l'affichage du plateau {i}: {e}")

        # Si un plateau est en cours de déplacement, le dessiner à la position de la souris
        if self.dragging and self.dragged_plateau:
            x, y = pygame.mouse.get_pos()
            try:
                self.dessiner_plateau_miniature(
                    self.dragged_plateau,
                    x - taille_plateau_lateral//2,
                    y - taille_plateau_lateral//2,
                    taille_plateau_lateral
                )
            except Exception as e:
                print(f"Erreur lors de l'affichage du plateau déplacé: {e}")

        # Ajouter le bouton de confirmation si tous les plateaux sont placés
        tous_places = all(all(cell for cell in row) for row in self.dropped_plateaux)
        if tous_places:
            bouton_confirmer = pygame.Rect(
                (self.LARGEUR - 300 * self.RATIO_X) // 2,
                debut_y_central + taille_plateau_central + 20 * self.RATIO_Y,
                300 * self.RATIO_X,
                60 * self.RATIO_Y
            )
            pygame.draw.rect(self.ecran, self.VERT, bouton_confirmer)
            pygame.draw.rect(self.ecran, self.BLANC, bouton_confirmer, 2)
            
            police = pygame.font.Font(None, int(48 * min(self.RATIO_X, self.RATIO_Y)))
            texte = police.render("Confirmer", True, self.BLANC)
            rect_texte = texte.get_rect(center=bouton_confirmer.center)
            self.ecran.blit(texte, rect_texte)
            
            return bouton_confirmer
        return None

    def dessiner_plateau_miniature(self, nom_fichier, x, y, taille):
        """Méthode utilitaire pour dessiner un plateau miniature avec transformations"""
        with open(f"plateaux/{nom_fichier}", 'r') as f:
            plateau_data = json.load(f)
            # Appliquer les transformations
            plateau_transforme = self.appliquer_transformations(plateau_data, nom_fichier)
            taille_tuile = taille // 4
            
            # Fond du plateau
            rect = pygame.Rect(x, y, taille, taille)
            pygame.draw.rect(self.ecran, (60, 60, 60), rect)
            
            # Dessiner les tuiles
            for ligne in range(4):
                for col in range(4):
                    chemin_image = plateau_transforme[ligne][col]
                    tuile_rect = pygame.Rect(
                        x + (col * taille_tuile),
                        y + (ligne * taille_tuile),
                        taille_tuile,
                        taille_tuile
                    )
                    
                    if chemin_image:
                        couleur = (self.ROUGE if "rouge" in chemin_image else
                                 self.BLEU if "bleue" in chemin_image else
                                 self.JAUNE if "jaune" in chemin_image else
                                 self.VERT)
                        image = pygame.transform.scale(
                            self.images[couleur],
                            (taille_tuile, taille_tuile)
                        )
                        self.ecran.blit(image, tuile_rect)
                    pygame.draw.rect(self.ecran, self.BLANC, tuile_rect, 1)

    def get_plateau_rect(self, plateau):
        """Retourne le rectangle d'un plateau sélectionné dans la vue latérale."""
        taille_plateau_lateral = int(250 * min(self.RATIO_X, self.RATIO_Y))
        plateaux_non_deposes = [p for p in self.plateaux_selectionnes if not any(p in row for row in self.dropped_plateaux)]
        
        try:
            idx = plateaux_non_deposes.index(plateau)
            if idx < 2:  # Gauche
                x = int(50 * self.RATIO_X)
                y = int((self.HAUTEUR // 4) + (idx * taille_plateau_lateral * 1.2))
            else:  # Droite
                x = self.LARGEUR - int(50 * self.RATIO_X) - taille_plateau_lateral
                y = int((self.HAUTEUR // 4) + ((idx-2) * taille_plateau_lateral * 1.2))
            
            return pygame.Rect(x, y, taille_plateau_lateral, taille_plateau_lateral)
        except ValueError:
            return None

    def get_grid_cell_rect(self, i, j):
        """Retourne le rectangle d'une cellule de la grille centrale 2x2."""
        taille_plateau_central = int(1050 * min(self.RATIO_X, self.RATIO_Y))  # Mise à jour de la taille
        taille_quadrant = taille_plateau_central // 2
        
        debut_x_central = (self.LARGEUR - taille_plateau_central) // 2
        debut_y_central = (self.HAUTEUR - taille_plateau_central) // 2
        
        return pygame.Rect(
            debut_x_central + j * taille_quadrant,
            debut_y_central + i * taille_quadrant,
            taille_quadrant,
            taille_quadrant
        )

    def executer(self):
        en_cours = True
        self.mode = "selection"
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    
                    if self.mode == "selection":
                        # Navigation entre les pages
                        if self.nombre_pages > 1:
                            prec_rect = pygame.Rect(
                                int(self.debut_x - 100 * self.RATIO_X),
                                int(self.debut_y + self.total_hauteur//2),
                                int(50 * self.RATIO_X),
                                int(50 * self.RATIO_Y)
                            )
                            suiv_rect = pygame.Rect(
                                int(self.debut_x + self.total_largeur + 50 * self.RATIO_X),
                                int(self.debut_y + self.total_hauteur//2),
                                int(50 * self.RATIO_X),
                                int(50 * self.RATIO_Y)
                            )
                            
                            if prec_rect.collidepoint(x, y) and self.page_courante > 0:
                                self.page_courante -= 1
                                continue
                                
                            if suiv_rect.collidepoint(x, y) and self.page_courante < self.nombre_pages - 1:
                                self.page_courante += 1
                                continue
                        
                        retour_rect, suivant_rect = self.dessiner_ecran_selection()
                        
                        if suivant_rect and suivant_rect.collidepoint(x, y):
                            self.mode = "placement"
                            continue
                            
                        if retour_rect.collidepoint(x, y):
                            return None
                        
                        # Vérifier les clics sur les boutons de rotation et miroir
                        debut_index = self.page_courante * 8
                        for idx in range(len(self.boutons_rotation_gauche)):
                            index_reel = debut_index + idx
                            if index_reel < len(self.plateaux_sauvegardes):
                                plateau_nom = self.plateaux_sauvegardes[index_reel]
                                
                                # Rotation gauche (anti-horaire)
                                if self.boutons_rotation_gauche[idx].collidepoint(x, y):
                                    if plateau_nom not in self.plateaux_transformations:
                                        self.plateaux_transformations[plateau_nom] = {'rotation': 0, 'mirroir': False}
                                    self.plateaux_transformations[plateau_nom]['rotation'] = (self.plateaux_transformations[plateau_nom]['rotation'] - 90) % 360
                                    continue
                                
                                # Rotation droite (horaire)
                                if self.boutons_rotation_droite[idx].collidepoint(x, y):
                                    if plateau_nom not in self.plateaux_transformations:
                                        self.plateaux_transformations[plateau_nom] = {'rotation': 0, 'mirroir': False}
                                    self.plateaux_transformations[plateau_nom]['rotation'] = (self.plateaux_transformations[plateau_nom]['rotation'] + 90) % 360
                                    continue
                                
                                # Miroir
                                if self.boutons_miroir[idx].collidepoint(x, y):
                                    if plateau_nom not in self.plateaux_transformations:
                                        self.plateaux_transformations[plateau_nom] = {'rotation': 0, 'mirroir': False}
                                    self.plateaux_transformations[plateau_nom]['mirroir'] = not self.plateaux_transformations[plateau_nom]['mirroir']
                                    continue
                            
                        # Sélection des plateaux
                        for idx, rect in enumerate(self.boutons_plateaux):
                            if rect.collidepoint(x, y):
                                index_reel = self.page_courante * 8 + idx
                                if index_reel < len(self.plateaux_sauvegardes):
                                    plateau = self.plateaux_sauvegardes[index_reel]
                                    if plateau in self.plateaux_selectionnes:
                                        self.plateaux_selectionnes.remove(plateau)
                                    elif len(self.plateaux_selectionnes) < self.NOMBRE_PLATEAUX_REQUIS:
                                        self.plateaux_selectionnes.append(plateau)
                    
                    elif self.mode == "placement":
                        # Gestion du drag and drop
                        for plateau in self.plateaux_selectionnes:
                            rect = self.get_plateau_rect(plateau)
                            # Vérifier d'abord les plateaux déjà déposés
                            est_depose = False
                            for i in range(2):
                                for j in range(2):
                                    if self.dropped_plateaux[i][j] == plateau:
                                        grid_rect = self.get_grid_cell_rect(i, j)
                                        if grid_rect.collidepoint(x, y):
                                            self.dragging = True
                                            self.dragged_plateau = plateau
                                            self.dropped_plateaux[i][j] = None
                                            est_depose = True
                                            break
                                if est_depose:
                                    break
                            
                            # Si le plateau n'est pas déposé, vérifier les plateaux latéraux
                            if not est_depose and rect and rect.collidepoint(x, y):
                                self.dragging = True
                                self.dragged_plateau = plateau
                                break
                
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.mode == "placement" and self.dragging:
                        x, y = event.pos
                        deposé = False
                        for i in range(2):
                            for j in range(2):
                                rect = self.get_grid_cell_rect(i, j)
                                if rect.collidepoint(x, y):
                                    # Si la case est occupée, échanger les plateaux
                                    if self.dropped_plateaux[i][j]:
                                        plateau_existant = self.dropped_plateaux[i][j]
                                        self.dropped_plateaux[i][j] = self.dragged_plateau
                                        self.dragged_plateau = None
                                        self.dragging = False
                                        deposé = True
                                    else:
                                        self.dropped_plateaux[i][j] = self.dragged_plateau
                                        self.dragged_plateau = None
                                        self.dragging = False
                                        deposé = True
                                    break
                            if deposé:
                                break
                        
                        # Si le plateau n'a pas été déposé, il retourne à sa position d'origine
                        if not deposé:
                            self.dragging = False
                            self.dragged_plateau = None
            
            # Affichage selon le mode
            if self.mode == "selection":
                self.dessiner_ecran_selection()
            elif self.mode == "placement":
                bouton_confirmer = self.afficher_ecran_final(self.plateaux_selectionnes)
                
                # Si le bouton confirmer existe et est cliqué
                if (bouton_confirmer and event.type == pygame.MOUSEBUTTONDOWN and 
                    event.button == 1 and bouton_confirmer.collidepoint(x, y)):
                    # Créer le plateau final 8x8
                    plateau_final = [["assets/image_jaune.png" for _ in range(8)] for _ in range(8)]
                    
                    # Pour chaque plateau 2x2 dans la grille
                    for i in range(2):
                        for j in range(2):
                            if self.dropped_plateaux[i][j]:
                                # Charger les données du plateau
                                with open(f"plateaux/{self.dropped_plateaux[i][j]}", 'r') as f:
                                    plateau_data = json.load(f)
                                    
                                    # Appliquer les transformations au plateau
                                    plateau_transforme = self.appliquer_transformations(plateau_data, self.dropped_plateaux[i][j])
                                    
                                    # Vérifier la taille du plateau source
                                    taille_source = len(plateau_transforme)
                                    
                                    # Calculer les offsets pour le placement dans le plateau final
                                    offset_ligne = i * 4
                                    offset_col = j * 4
                                    
                                    # Copier les cases du plateau transformé dans le plateau final
                                    for ligne_source in range(min(4, taille_source)):
                                        for col_source in range(min(4, len(plateau_transforme[ligne_source]))):
                                            ligne_finale = offset_ligne + ligne_source
                                            col_finale = offset_col + col_source
                                            plateau_final[ligne_finale][col_finale] = plateau_transforme[ligne_source][col_source]
                      # Sauvegarder le plateau dans le fichier unique plateau_final/plateau_finale.json
                    try:
                        with open(os.path.join("plateau_final", "plateau_finale.json"), 'w') as f:
                            json.dump(plateau_final, f, indent=4)
                    except Exception as e:
                        print(f"Erreur lors de la sauvegarde du plateau: {e}")
                    
                    return self.dropped_plateaux
            
            pygame.display.flip()

if __name__ == "__main__":
    selecteur = SelecteurPlateau()
    plateaux_choisis = selecteur.executer()
    if plateaux_choisis:
        print(f"Plateaux sélectionnés : {plateaux_choisis}")
    else:
        print("Aucun plateau sélectionné")
    pygame.quit()
