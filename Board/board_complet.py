import pygame
import json
import os
import sys

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
        
        # Charger la liste initiale
        self.charger_liste_plateaux()

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

    def dessiner_ecran_selection(self):
        self.ecran.fill(self.NOIR)
        
        # Titre
        police = pygame.font.Font(None, int(48 * min(self.RATIO_X, self.RATIO_Y)))
        titre = police.render("Sélectionnez un plateau", True, self.BLANC)
        titre_rect = titre.get_rect(centerx=self.LARGEUR // 2, y=int(30 * self.RATIO_Y))
        self.ecran.blit(titre, titre_rect)
        
        # Dimensions des miniatures
        taille_miniature = int(300 * min(self.RATIO_X, self.RATIO_Y))
        espace = int(50 * min(self.RATIO_X, self.RATIO_Y))
        
        # Calcul pour centrer la grille 4x2
        self.total_largeur = (taille_miniature * 4) + (espace * 3)
        self.total_hauteur = (taille_miniature * 2) + espace
        
        self.debut_x = (self.LARGEUR - self.total_largeur) // 2
        self.debut_y = (self.HAUTEUR - self.total_hauteur) // 2
        
        # Afficher les miniatures
        debut_index = self.page_courante * 8
        self.boutons_plateaux = []
        
        for i in range(min(8, len(self.plateaux_sauvegardes) - debut_index)):
            ligne = i // 4
            colonne = i % 4
            x = self.debut_x + colonne * (taille_miniature + espace)
            y = self.debut_y + ligne * (taille_miniature + espace)
            
            rect = pygame.Rect(x, y, taille_miniature, taille_miniature)
            self.boutons_plateaux.append(rect)
            
            # Fond et bordure
            pygame.draw.rect(self.ecran, (60, 60, 60), rect)
            pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
            
            # Afficher la prévisualisation
            index = debut_index + i
            try:
                with open(f"plateaux/{self.plateaux_sauvegardes[index]}", 'r') as f:
                    plateau_data = json.load(f)
                    taille_tuile = taille_miniature // 4
                    
                    for ligne_p in range(4):
                        for col_p in range(4):
                            chemin_image = plateau_data[ligne_p][col_p]
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
                print(f"Erreur lors du chargement de la miniature {index}: {e}")

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
        
        return retour_rect

    def executer(self):
        en_cours = True
        plateau_selectionne = None
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    # Gestion du retour
                    retour_rect = pygame.Rect(
                        int(50 * self.RATIO_X),
                        int(50 * self.RATIO_Y),
                        int(200 * self.RATIO_X),
                        int(50 * self.RATIO_Y)
                    )
                    if retour_rect.collidepoint(x, y):
                        return None
                    
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
                    
                    # Sélection d'un plateau
                    for idx, rect in enumerate(self.boutons_plateaux):
                        if rect.collidepoint(x, y):
                            index_reel = self.page_courante * 8 + idx
                            if index_reel < len(self.plateaux_sauvegardes):
                                return self.plateaux_sauvegardes[index_reel]
            
            self.dessiner_ecran_selection()
            pygame.display.flip()
        
        return None

if __name__ == "__main__":
    selecteur = SelecteurPlateau()
    plateau_choisi = selecteur.executer()
    if plateau_choisi:
        print(f"Plateau sélectionné : {plateau_choisi}")
    else:
        print("Aucun plateau sélectionné")
    pygame.quit()