import pygame
import sys
import json
import os

class EditeurPlateau4x4:
    def __init__(self):
        # Initialiser Pygame
        pygame.init()
        
        self.font_path = pygame.font.match_font('assets/police-gloomie_saturday/Gloomie Saturday.otf')
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        
        # Fond d'écran
        self.background_image = pygame.image.load("assets/menu-claire/fond-menu-editeur.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        
        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440
        
        # Taille de base des éléments
        self.TAILLE_BASE_CASE = 280
        self.TAILLE_BASE_BOUTON = 140
        self.MARGE_BASE = 50
        
        # page chargement
        self.page_courante = 0
        
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
        
        # Configuration du plateau adaptée
        self.TAILLE_PLATEAU = 4
        self.TAILLE_CASE = int(self.TAILLE_BASE_CASE * min(self.RATIO_X, self.RATIO_Y))
        self.couleurs_disponibles = [self.ROUGE, self.BLEU, self.JAUNE, self.VERT]
        self.couleur_selectionnee = self.ROUGE
        
        # Position du plateau (centrée)
        self.plateau_x = int(self.LARGEUR * 0.28)
        self.plateau_y = int(self.HAUTEUR * 0.11)
        
        # Initialisation de l'écran - DÉPLACÉ ICI
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Éditeur de Plateau 4x4")
        
        # Chargement des images - DÉPLACÉ APRÈS L'INITIALISATION DE L'ÉCRAN
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
        
        # Création du plateau vide
        self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                    for _ in range(self.TAILLE_PLATEAU)]
        
        # État de l'interface
        self.mode = "editeur"
        self.plateaux_sauvegardes = []
        self.boutons_plateaux = []
        
        # Boutons
        self.boutons = self._creer_boutons()
        self.bouton_retour = {
        "rect": pygame.Rect(int(50 * self.RATIO_X), int(50 * self.RATIO_Y), 120, 40),
        "couleur": self.ROUGE,
        "texte": "Retour"
        }

    def _creer_boutons(self):
        boutons = {}
        
        # Calcul des dimensions adaptées
        taille_bouton_couleur = int(self.TAILLE_BASE_BOUTON * min(self.RATIO_X, self.RATIO_Y))
        espace_couleur = int(150 * self.RATIO_Y)
        x_couleur = int(360 * self.RATIO_X)
        y_couleur = int(450 * self.RATIO_Y)
        
        # Boutons de couleurs
        for i, couleur in enumerate(self.couleurs_disponibles):
            boutons[f"couleur_{i}"] = {
                "rect": pygame.Rect(x_couleur, y_couleur + i*espace_couleur,
                                  taille_bouton_couleur, taille_bouton_couleur),
                "couleur": couleur,
                "action": "select_color"
            }
        
        # Boutons d'action
        largeur_bouton = int(225 * self.RATIO_X)
        hauteur_bouton = int(60 * self.RATIO_Y)
        x_action = int(self.LARGEUR * 0.815)  
        
        boutons_actions = [
            ("sauvegarder", self.NOIR, "Sauvegarder", "save", 550),
            ("charger", self.NOIR, "Charger", "load", 690),
            ("effacer", self.NOIR, "Effacer tout", "clear", 830)
        ]
        
        for nom, couleur, texte, action, y in boutons_actions:
            boutons[nom] = {
                "rect": pygame.Rect(x_action, int(y * self.RATIO_Y),
                                  largeur_bouton, hauteur_bouton),
                "couleur": couleur,
                "texte": texte,
                "action": action
            }
        
        return boutons

    def charger_liste_plateaux(self):
        self.plateaux_sauvegardes = []
        self.boutons_plateaux = []
        
        if not os.path.exists("plateaux"):
            os.makedirs("plateaux")
            
        # Charger tous les fichiers JSON
        self.plateaux_sauvegardes = [f for f in os.listdir("plateaux") if f.endswith('.json')]
        
        # Calculer le nombre total de pages
        self.nombre_pages = (len(self.plateaux_sauvegardes) + 7) // 8

    def dessiner_ecran_selection(self):
        self.ecran.blit(self.background_image, (0, 0))
        
        
        police_titre = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 23)
        
        # Titre
        police = pygame.font.Font(None, int(48 * min(self.RATIO_X, self.RATIO_Y)))
        titre = police_titre.render("Selectionnez un plateau", True, self.BLANC)
        titre_rect = titre.get_rect(centerx=self.LARGEUR // 2, y=int(80 * self.RATIO_Y))
        self.ecran.blit(titre, titre_rect)
        
        # Augmentation de 100% de la taille
        taille_miniature = int(300 * min(self.RATIO_X, self.RATIO_Y))
        espace = int(50 * min(self.RATIO_X, self.RATIO_Y))
        
        # Calcul pour centrer la grille 4x2
        self.total_largeur = (taille_miniature * 4) + (espace * 3)
        self.total_hauteur = (taille_miniature * 2) + espace
        
        self.debut_x = (self.LARGEUR - self.total_largeur) // 2
        self.debut_y = (self.HAUTEUR - self.total_hauteur) // 2

        # Afficher les miniatures de la page courante
        self.boutons_plateaux = []
        debut_index = self.page_courante * 8

        # Charger la liste des plateaux si elle est vide
        if not self.plateaux_sauvegardes:
            self.charger_liste_plateaux()
        
        for i in range(min(8, len(self.plateaux_sauvegardes) - debut_index)):
            ligne = i // 4
            colonne = i % 4
            x = self.debut_x + colonne * (taille_miniature + espace)
            y = self.debut_y + ligne * (taille_miniature + espace)
            
            rect = pygame.Rect(x, y, taille_miniature, taille_miniature)
            self.boutons_plateaux.append(rect)
            
            # Dessiner le fond et la bordure
            pygame.draw.rect(self.ecran, (60, 60, 60), rect)
            pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
            
            # Afficher le plateau
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
                                image = pygame.transform.scale(
                                    self.images[self.ROUGE if "rouge" in chemin_image else
                                            self.BLEU if "bleue" in chemin_image else
                                            self.JAUNE if "jaune" in chemin_image else
                                            self.VERT],
                                    (taille_tuile, taille_tuile)
                                )
                                self.ecran.blit(image, tuile_rect)
                            pygame.draw.rect(self.ecran, self.BLANC, tuile_rect, 1)
            except Exception as e:
                print(f"Erreur lors du chargement de la miniature {index}: {e}")

        # Boutons de navigation (si plusieurs pages)
        if self.nombre_pages > 1:
            # Définir les rectangles pour les boutons de navigation
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

            police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
            
            # Bouton précédent
            if self.page_courante > 0:
                pygame.draw.rect(self.ecran, self.BLEU, prec_rect)
                texte = police.render("<", True, self.BLANC)
                rect_texte = texte.get_rect(center=prec_rect.center)
                self.ecran.blit(texte, rect_texte)
            
            # Bouton suivant
            if self.page_courante < self.nombre_pages - 1:
                pygame.draw.rect(self.ecran, self.BLEU, suiv_rect)
                texte = police.render(">", True, self.BLANC)
                rect_texte = texte.get_rect(center=suiv_rect.center)
                self.ecran.blit(texte, rect_texte)

        # Bouton Retour (style identique menu/settings)
        retour_rect = pygame.Rect(
            int(50 * self.RATIO_X),
            int(50 * self.RATIO_Y),
            120, 40
        )
        pygame.draw.rect(self.ecran, self.ROUGE, retour_rect, border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, retour_rect, 2, border_radius=15)
        police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        texte_retour = police_retour.render("Retour", True, self.BLANC)
        rect_texte = texte_retour.get_rect(center=retour_rect.center)
        self.ecran.blit(texte_retour, rect_texte)

        # Bouton Nouveau arrondi
        nouveau_rect = pygame.Rect(
            titre_rect.right + 30,  # 30 pixels d'espace après le titre
            titre_rect.y + (titre_rect.height // 2) - int(25 * self.RATIO_Y),  # centré verticalement sur le titre
            int(200 * self.RATIO_X),
            int(50 * self.RATIO_Y)
        )
        pygame.draw.rect(self.ecran, self.NOIR, nouveau_rect, border_radius=20)
        pygame.draw.rect(self.ecran, self.BLANC, nouveau_rect, 2, border_radius=20)
        texte_nouveau = police_bouton.render("Nouveau", True, self.BLANC)
        rect_texte_nouveau = texte_nouveau.get_rect(center=nouveau_rect.center)
        self.ecran.blit(texte_nouveau, rect_texte_nouveau)

        return retour_rect, nouveau_rect

    def dessiner(self):
        # Afficher l'image d'arrière-plan
        self.ecran.blit(self.background_image, (0, 0))
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 23)
        
        # Dessiner le plateau
        for ligne in range(self.TAILLE_PLATEAU):
            for colonne in range(self.TAILLE_PLATEAU):
                x = self.plateau_x + colonne * self.TAILLE_CASE
                y = self.plateau_y + ligne * self.TAILLE_CASE
                
                rect = pygame.Rect(x, y, self.TAILLE_CASE, self.TAILLE_CASE)
                couleur = self.plateau[ligne][colonne]
                
                # Draw background
                pygame.draw.rect(self.ecran, self.NOIR, rect)
                
                # Draw image if available, otherwise use color
                if couleur in self.images:
                    image = pygame.transform.scale(self.images[couleur], 
                                                (self.TAILLE_CASE, self.TAILLE_CASE))
                    self.ecran.blit(image, rect)
                else:
                    pygame.draw.rect(self.ecran, couleur, rect)
                
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
        
        # Dessiner les boutons
        for key, info_bouton in self.boutons.items():
            rect = info_bouton["rect"]
            couleur = info_bouton["couleur"]

            # Boutons arrondis noirs avec contour blanc
            pygame.draw.rect(self.ecran, self.NOIR, rect, border_radius=20)
            pygame.draw.rect(self.ecran, self.BLANC, rect, 2, border_radius=20)

            # Pour les boutons de sélection de couleur, affiche l'image si dispo
            if info_bouton["action"] == "select_color" and couleur in self.images:
                image = pygame.transform.scale(self.images[couleur], 
                                            (rect.width, rect.height))
                self.ecran.blit(image, rect)
            else:
                pygame.draw.rect(self.ecran, couleur, rect, border_radius=20)
            
            # Highlight selected color
            if (info_bouton["action"] == "select_color" and 
                info_bouton["couleur"] == self.couleur_selectionnee):
                pygame.draw.rect(self.ecran, self.BLANC, rect, 4, border_radius=20)
                
                triangle_size = int(30 * min(self.RATIO_X, self.RATIO_Y))
                triangle_x = rect.x - triangle_size - 10
                triangle_y = rect.centery
                
                points = [
                    (triangle_x, triangle_y - triangle_size//2),
                    (triangle_x, triangle_y + triangle_size//2),
                    (triangle_x + triangle_size, triangle_y)
                ]
                pygame.draw.polygon(self.ecran, self.BLANC, points)
            
            # Texte des boutons d'action avec police personnalisée
            if "texte" in info_bouton:
                texte = police_bouton.render(info_bouton["texte"], True, self.BLANC)
                rect_texte = texte.get_rect(center=rect.center)
                self.ecran.blit(texte, rect_texte)

        # Bouton retour (identique à settings.py)
        pygame.draw.rect(self.ecran, self.bouton_retour["couleur"], self.bouton_retour["rect"], border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour["rect"], 2, border_radius=15)
        police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        texte_retour = police_retour.render(self.bouton_retour["texte"], True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
        self.ecran.blit(texte_retour, rect_texte_retour)

    def sauvegarder_plateau(self):
        # Vérifier que toutes les cases sont remplies
        for ligne in self.plateau:
            for case in ligne:
                if case == self.NOIR:
                    print("Erreur: Toutes les cases doivent être remplies avant de sauvegarder!")
                    # Effet visuel d'erreur : rectangle rouge arrondi
                    bouton = self.boutons["sauvegarder"]
                    pygame.draw.rect(self.ecran, self.ROUGE, bouton["rect"], 4, border_radius=20)
                    pygame.display.flip()
                    pygame.time.delay(300)
                    return
        
        if not os.path.exists("plateaux"):
            os.makedirs("plateaux")
            
        try:
            # Créer un dictionnaire inverse pour obtenir les chemins d'images depuis les couleurs
            couleur_vers_image = {
                self.ROUGE: "assets/image_rouge.png",
                self.BLEU: "assets/image_bleue.png",
                self.JAUNE: "assets/image_jaune.png",
                self.VERT: "assets/image_verte.png"
            }
            
            # Convertir le plateau en chemins d'images
            plateau_images = []
            for ligne in self.plateau:
                ligne_images = []
                for couleur in ligne:
                    ligne_images.append(couleur_vers_image[couleur])  # On sait que toutes les cases ont une couleur
                plateau_images.append(ligne_images)
            
            # Déterminer le nom du fichier
            if hasattr(self, 'fichier_charge'):
                # Si un plateau a été chargé, on l'écrase
                nom_fichier = f"plateaux/{self.fichier_charge}"
            else:
                # Sinon, on crée un nouveau fichier
                num = len([f for f in os.listdir("plateaux") if f.endswith('.json')])
                nom_fichier = f"plateaux/plateau_{num}.json"
            
            with open(nom_fichier, 'w') as f:
                json.dump(plateau_images, f)
                
            # Recharger la liste et aller à la dernière page
            self.charger_liste_plateaux()
            self.page_courante = (len(self.plateaux_sauvegardes) - 1) // 8
            print(f"Plateau sauvegardé sous {nom_fichier}!")
            
            # Effet visuel de confirmation
            bouton = self.boutons["sauvegarder"]
            pygame.draw.rect(self.ecran, self.BLANC, bouton["rect"], 4)
            pygame.display.flip()
            pygame.time.delay(300)
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            
            # Effet visuel de confirmation
            bouton = self.boutons["sauvegarder"]
            pygame.draw.rect(self.ecran, self.BLANC, bouton["rect"], 4)
            pygame.display.flip()
            pygame.time.delay(300)
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def charger_plateau(self, nom_fichier):
        try:
            # Dictionnaire pour convertir les chemins d'images en couleurs
            image_vers_couleur = {
                "assets/image_rouge.png": self.ROUGE,
                "assets/image_bleue.png": self.BLEU,
                "assets/image_jaune.png": self.JAUNE,
                "assets/image_verte.png": self.VERT
            }
            
            with open(f"plateaux/{nom_fichier}", 'r') as f:
                plateau_images = json.load(f)
                
                # Convertir les chemins d'images en couleurs
                self.plateau = []
                for ligne in plateau_images:
                    ligne_couleurs = []
                    for chemin in ligne:
                        ligne_couleurs.append(image_vers_couleur[chemin])
                    self.plateau.append(ligne_couleurs)
            
            # Sauvegarder le nom du fichier chargé
            self.fichier_charge = nom_fichier
            print("Plateau chargé avec succès!")
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")

    def executer(self):
        en_cours = True
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    if self.mode == "editeur":
                        menu_rect = pygame.Rect(
                            int(50 * self.RATIO_X),
                            int(50 * self.RATIO_Y),
                            int(200 * self.RATIO_X),
                            int(50 * self.RATIO_Y)
                        )
                        if menu_rect.collidepoint(x, y):
                            return
                            
                        # Vérifier les clics sur le plateau
                        if (self.plateau_x <= x < self.plateau_x + self.TAILLE_PLATEAU * self.TAILLE_CASE and
                            self.plateau_y <= y < self.plateau_y + self.TAILLE_PLATEAU * self.TAILLE_CASE):
                            colonne = (x - self.plateau_x) // self.TAILLE_CASE
                            ligne = (y - self.plateau_y) // self.TAILLE_CASE
                            self.plateau[ligne][colonne] = self.couleur_selectionnee
                        
                        # Vérifier les clics sur les boutons
                        for info_bouton in self.boutons.values():
                            if info_bouton["rect"].collidepoint(x, y):
                                if info_bouton["action"] == "select_color":
                                    self.couleur_selectionnee = info_bouton["couleur"]
                                elif info_bouton["action"] == "save":
                                    self.sauvegarder_plateau()
                                elif info_bouton["action"] == "load":
                                    self.mode = "selection"
                                    self.charger_liste_plateaux()
                                elif info_bouton["action"] == "clear":
                                    self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                                                  for _ in range(self.TAILLE_PLATEAU)]
                    
                    elif self.mode == "selection":
                        # Vérifier le clic sur le bouton retour
                        if self.nombre_pages > 1:
                            prec_rect = pygame.Rect(
                                int((self.LARGEUR - self.total_largeur) // 2 - 100 * self.RATIO_X),
                                int(self.debut_y + self.total_hauteur//2),
                                int(50 * self.RATIO_X),
                                int(50 * self.RATIO_Y)
                            )
                            suiv_rect = pygame.Rect(
                                int((self.LARGEUR + self.total_largeur) // 2 + 50 * self.RATIO_X),
                                int(self.debut_y + self.total_hauteur//2),
                                int(50 * self.RATIO_X),
                                int(50 * self.RATIO_Y)
                            )
                            
                            if prec_rect.collidepoint(x, y) and self.page_courante > 0:
                                self.page_courante -= 1
                                pygame.display.flip()
                                continue
                                
                            if suiv_rect.collidepoint(x, y) and self.page_courante < self.nombre_pages - 1:
                                self.page_courante += 1
                                pygame.display.flip()
                                continue
                            
                        retour_rect = pygame.Rect(
                            int(50 * self.RATIO_X),
                            int(50 * self.RATIO_Y),
                            int(200 * self.RATIO_X),
                            int(50 * self.RATIO_Y)
                        )
                        nouveau_rect = pygame.Rect(
                            int(self.LARGEUR * 0.7),
                            int(50 * self.RATIO_Y),
                            int(200 * self.RATIO_X),
                            int(50 * self.RATIO_Y)
                        )
                        if retour_rect.collidepoint(x, y):
                            self.mode = "editeur"
                        elif nouveau_rect.collidepoint(x, y):
                            # Réinitialiser le plateau et le fichier chargé
                            self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                                        for _ in range(self.TAILLE_PLATEAU)]
                            if hasattr(self, 'fichier_charge'):
                                delattr(self, 'fichier_charge')
                            self.mode = "editeur"
                            
                        for idx, rect in enumerate(self.boutons_plateaux):
                            if rect.collidepoint(x, y):
                                # Calculer l'index réel en tenant compte de la page courante
                                index_reel = self.page_courante * 8 + idx
                                if index_reel < len(self.plateaux_sauvegardes):
                                    self.charger_plateau(self.plateaux_sauvegardes[index_reel])
                                    self.mode = "editeur"
                                break
            
            if self.mode == "editeur":
                self.dessiner()
            else:
                self.dessiner_ecran_selection()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    editeur = EditeurPlateau4x4()
    editeur.executer()