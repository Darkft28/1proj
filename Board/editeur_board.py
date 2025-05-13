import pygame
import sys
import json
import os

class EditeurPlateau4x4:
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
        
        # Taille de base des éléments
        self.TAILLE_BASE_CASE = 280
        self.TAILLE_BASE_BOUTON = 140
        self.MARGE_BASE = 50
        
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
        x_action = int(self.LARGEUR * 0.815)  # ~2088/2560
        
        boutons_actions = [
            ("sauvegarder", self.VERT, "Sauvegarder", "save", 550),
            ("charger", self.BLEU, "Charger", "load", 690),
            ("effacer", self.ROUGE, "Effacer tout", "clear", 830)
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
        y_pos = int(100 * self.RATIO_Y)
        
        if not os.path.exists("plateaux"):
            os.makedirs("plateaux")
            
        for fichier in os.listdir("plateaux"):
            if fichier.endswith('.json'):
                rect = pygame.Rect(
                    int(50 * self.RATIO_X),
                    y_pos,
                    int(700 * self.RATIO_X),
                    int(60 * self.RATIO_Y)
                )
                self.plateaux_sauvegardes.append(fichier)
                self.boutons_plateaux.append(rect)
                y_pos += int(80 * self.RATIO_Y)

    def dessiner_ecran_selection(self):
        self.ecran.fill(self.NOIR)
        
        # Titre
        police = pygame.font.Font(None, int(48 * min(self.RATIO_X, self.RATIO_Y)))
        titre = police.render("Sélectionnez un plateau", True, self.BLANC)
        self.ecran.blit(titre, (int(50 * self.RATIO_X), int(30 * self.RATIO_Y)))

        # Dessiner les plateaux sauvegardés
        if not self.plateaux_sauvegardes:
            texte = police.render("Aucun plateau sauvegardé", True, self.BLANC)
            self.ecran.blit(texte, (int(50 * self.RATIO_X), int(100 * self.RATIO_Y)))
        else:
            police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
            for idx, fichier in enumerate(self.plateaux_sauvegardes):
                rect = self.boutons_plateaux[idx]
                pygame.draw.rect(self.ecran, self.BLEU, rect)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
                
                texte = police.render(fichier, True, self.BLANC)
                self.ecran.blit(texte, (rect.x + int(20 * self.RATIO_X), rect.y + int(20 * self.RATIO_Y)))

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
        self.ecran.blit(texte, (
            retour_rect.x + int(60 * self.RATIO_X),
            retour_rect.y + int(15 * self.RATIO_Y)
        ))
        
        return retour_rect

    def dessiner(self):
        self.ecran.fill(self.NOIR)
        
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
            
            # Draw button background
            pygame.draw.rect(self.ecran, self.NOIR, rect)
            
            # For color selection buttons, draw the image if available
            if info_bouton["action"] == "select_color" and couleur in self.images:
                image = pygame.transform.scale(self.images[couleur], 
                                            (rect.width, rect.height))
                self.ecran.blit(image, rect)
            else:
                pygame.draw.rect(self.ecran, couleur, rect)
            
            pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
            
            # Highlight selected color
            if (info_bouton["action"] == "select_color" and 
                info_bouton["couleur"] == self.couleur_selectionnee):
                pygame.draw.rect(self.ecran, self.BLANC, rect, 4)
                
                triangle_size = int(30 * min(self.RATIO_X, self.RATIO_Y))
                triangle_x = rect.x - triangle_size - 10
                triangle_y = rect.centery
                
                points = [
                    (triangle_x, triangle_y - triangle_size//2),
                    (triangle_x, triangle_y + triangle_size//2),
                    (triangle_x + triangle_size, triangle_y)
                ]
                pygame.draw.polygon(self.ecran, self.BLANC, points)
            
            # Draw button text if present
            if "texte" in info_bouton:
                police = pygame.font.Font(None, int(30 * min(self.RATIO_X, self.RATIO_Y)))
                texte = police.render(info_bouton["texte"], True, self.BLANC)
                rect_texte = texte.get_rect(center=rect.center)
                self.ecran.blit(texte, rect_texte)
        
        menu_rect = pygame.Rect(
            int(50 * self.RATIO_X),
            int(50 * self.RATIO_Y),
            int(200 * self.RATIO_X),
            int(50 * self.RATIO_Y)
        )
        
        pygame.draw.rect(self.ecran, self.ROUGE, menu_rect)
        pygame.draw.rect(self.ecran, self.BLANC, menu_rect, 2)
        
        police = pygame.font.Font(None, int(36 * min(self.RATIO_X, self.RATIO_Y)))
        texte = police.render("Retour ", True, self.BLANC)
        rect_texte = texte.get_rect(center=menu_rect.center)
        self.ecran.blit(texte, rect_texte)

    # Les autres méthodes restent identiques car elles utilisent déjà les variables adaptatives
    def sauvegarder_plateau(self):
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
                    if couleur == self.NOIR:
                        ligne_images.append(None)  # Case vide
                    else:
                        ligne_images.append(couleur_vers_image.get(couleur, None))
                plateau_images.append(ligne_images)
            
            # Sauvegarder dans un fichier JSON
            num = len([f for f in os.listdir("plateaux") if f.endswith('.json')])
            nom_fichier = f"plateaux/plateau_{num}.json"
            with open(nom_fichier, 'w') as f:
                json.dump(plateau_images, f)
            print(f"Plateau sauvegardé sous {nom_fichier}!")
            
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
                        if chemin is None:
                            ligne_couleurs.append(self.NOIR)  # Case vide
                        else:
                            ligne_couleurs.append(image_vers_couleur.get(chemin, self.NOIR))
                    self.plateau.append(ligne_couleurs)
                    
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
                        retour_rect = pygame.Rect(
                            int(50 * self.RATIO_X),
                            int(50 * self.RATIO_Y),
                            int(200 * self.RATIO_X),
                            int(50 * self.RATIO_Y)
                        )
                        if retour_rect.collidepoint(x, y):
                            self.mode = "editeur"
                        
                        # Vérifier les clics sur les plateaux sauvegardés
                        for idx, rect in enumerate(self.boutons_plateaux):
                            if rect.collidepoint(x, y):
                                self.charger_plateau(self.plateaux_sauvegardes[idx])
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