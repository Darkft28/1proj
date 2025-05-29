import pygame
import sys
import json
import os
import pygame
import sys
import json
import os
from menu.config import get_theme

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
        theme = get_theme()
        if theme == "Sombre":
            self.background_image = pygame.image.load("assets/menu/menu-sombre.png")
        else:
            self.background_image = pygame.image.load("assets/menu/menu-claire.png")
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
        self.plateaux_selectionnes = set()
        self.mode_suppression = False
        self.plateau_modifie = False  # Pour suivre si des modifications ont été faites
        self.message_erreur = None  # Pour garder le message d'erreur affiché
        self.derniere_sauvegarde = None  # Pour comparer avec l'état actuel
        self.message_erreur_actif = False  # Pour gérer l'affichage persistant du message d'erreur
        self.message_succes = None  # Pour afficher le message de succès
        self.message_succes_actif = False  # Pour gérer l'affichage persistant du message de succès
        
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
            
        # Charger tous les fichiers JSON et les trier pour maintenir un ordre stable
        self.plateaux_sauvegardes = [f for f in os.listdir("plateaux") if f.endswith('.json')]
        # Trier par nom pour maintenir un ordre cohérent
        self.plateaux_sauvegardes.sort()
        
        # Calculer le nombre total de pages
        self.nombre_pages = max(1, (len(self.plateaux_sauvegardes) + 7) // 8)

    def dessiner_ecran_selection(self):
        self.ecran.blit(self.background_image, (0, 0))
        police_titre = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 23)
        
        # Titre
        titre = police_titre.render("Selectionnez un plateau", True, self.BLANC)
        titre_rect = titre.get_rect(centerx=self.LARGEUR // 2, y=int(80 * self.RATIO_Y))
        self.ecran.blit(titre, titre_rect)
          # Bouton Nouveau dans l'angle supérieur droit
        nouveau_rect = pygame.Rect(
            self.LARGEUR - int(250 * self.RATIO_X),  # Plus près du bord droit
            int(50 * self.RATIO_Y),
            int(200 * self.RATIO_X),
            int(50 * self.RATIO_Y)
        )
        pygame.draw.rect(self.ecran, self.NOIR, nouveau_rect, border_radius=20)
        pygame.draw.rect(self.ecran, self.BLANC, nouveau_rect, 2, border_radius=20)
        texte_nouveau = police_bouton.render("Nouveau", True, self.BLANC)
        rect_texte_nouveau = texte_nouveau.get_rect(center=nouveau_rect.center)
        self.ecran.blit(texte_nouveau, rect_texte_nouveau)

        # Bouton Supprimer à gauche de Nouveau
        supprimer_rect = pygame.Rect(
            self.LARGEUR - int(500 * self.RATIO_X),
            int(50 * self.RATIO_Y),
            int(200 * self.RATIO_X),
            int(50 * self.RATIO_Y)
        )
        pygame.draw.rect(self.ecran, self.ROUGE if not self.mode_suppression else self.VERT, supprimer_rect, border_radius=20)
        pygame.draw.rect(self.ecran, self.BLANC, supprimer_rect, 2, border_radius=20)
        texte_supprimer = police_bouton.render("Supprimer" if not self.mode_suppression else "Annuler", True, self.BLANC)
        rect_texte_supprimer = texte_supprimer.get_rect(center=supprimer_rect.center)
        self.ecran.blit(texte_supprimer, rect_texte_supprimer)
        
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
        self.boutons_supprimer = []
        debut_index = self.page_courante * 8
        
        # Vérifier si la liste des plateaux est vide
        if not self.plateaux_sauvegardes:
            self.charger_liste_plateaux()
        
        self.boutons_plateaux = []
        self.boutons_supprimer = []
        
        # Afficher les miniatures
        for i in range(min(8, len(self.plateaux_sauvegardes) - debut_index)):
            ligne = i // 4
            colonne = i % 4
            x = self.debut_x + colonne * (taille_miniature + espace)
            y = self.debut_y + ligne * (taille_miniature + espace)
            rect = pygame.Rect(x, y, taille_miniature, taille_miniature)
            self.boutons_plateaux.append(rect)
            
            index = debut_index + i
            
            # Afficher la prévisualisation du plateau
            try:
                with open(f"plateaux/{self.plateaux_sauvegardes[index]}", 'r') as f:
                    plateau_data = json.load(f)
                    taille_tuile = taille_miniature // 4
                    
                    for ligne_p in range(4):
                        for col_p in range(4):
                            tuile_rect = pygame.Rect(
                                x + (col_p * taille_tuile),
                                y + (ligne_p * taille_tuile),
                                taille_tuile,
                                taille_tuile
                            )
                            chemin_image = plateau_data[ligne_p][col_p]
                            
                            if chemin_image:
                                couleur = (
                                    self.ROUGE if "rouge" in chemin_image
                                    else self.BLEU if "bleue" in chemin_image
                                    else self.JAUNE if "jaune" in chemin_image
                                    else self.VERT
                                )
                                if couleur in self.images:
                                    image = pygame.transform.scale(
                                        self.images[couleur],
                                        (taille_tuile, taille_tuile)
                                    )
                                    self.ecran.blit(image, tuile_rect)
                            
                            pygame.draw.rect(self.ecran, self.BLANC, tuile_rect, 1)
                            
            except Exception as e:
                print(f"Erreur lors du chargement de la miniature {index}: {e}")
            
            # Afficher un cadre de sélection rouge APRÈS le contenu si le plateau est sélectionné pour suppression
            if self.mode_suppression and index in self.plateaux_selectionnes:
                pygame.draw.rect(self.ecran, self.ROUGE, rect, 6)  # Bordure plus épaisse pour plus de visibilité

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

        # Bouton Confirmer (visible uniquement en mode suppression avec des plateaux sélectionnés)
        confirmer_rect = None
        if self.mode_suppression and self.plateaux_selectionnes:
            confirmer_rect = pygame.Rect(
                self.LARGEUR//2 - int(200 * self.RATIO_X),
                self.HAUTEUR - int(100 * self.RATIO_Y),
                int(400 * self.RATIO_X),
                int(50 * self.RATIO_Y)
            )
            pygame.draw.rect(self.ecran, self.VERT, confirmer_rect, border_radius=20)
            pygame.draw.rect(self.ecran, self.BLANC, confirmer_rect, 2, border_radius=20)
            texte_confirmer = police_bouton.render(f"Confirmer ({len(self.plateaux_selectionnes)})", True, self.BLANC)
            rect_texte_confirmer = texte_confirmer.get_rect(center=confirmer_rect.center)
            self.ecran.blit(texte_confirmer, rect_texte_confirmer)

        # Bouton Retour (style identique menu/settings)
        retour_rect = pygame.Rect(
            int(50 * self.RATIO_X),
            int(50 * self.RATIO_Y),
            120, 40
        )
        pygame.draw.rect(self.ecran, self.ROUGE, retour_rect, border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, retour_rect, 2, border_radius=15)
        texte_retour = police_bouton.render("Retour", True, self.BLANC)
        rect_texte = texte_retour.get_rect(center=retour_rect.center)
        self.ecran.blit(texte_retour, rect_texte)

        return retour_rect, nouveau_rect, supprimer_rect, confirmer_rect

    def dessiner(self):
        """Dessine l'éditeur de plateau."""
        # Afficher l'image d'arrière-plan
        self.ecran.blit(self.background_image, (0, 0))
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 23)
        
        # Compter les couleurs utilisées
        comptes = self.compter_couleurs()
        
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
            
            if info_bouton["action"] == "select_color":
                # Dessiner le fond noir
                pygame.draw.rect(self.ecran, self.NOIR, rect)
                
                # Dessiner l'image de la couleur
                if couleur in self.images:
                    image = pygame.transform.scale(self.images[couleur], 
                                                (rect.width, rect.height))
                    self.ecran.blit(image, rect)
                
                # Vérifier si la couleur est épuisée
                est_epuisee = comptes.get(str(couleur), 0) >= 4 and self.couleur_selectionnee != couleur
                
                # Appliquer le filtre gris si la couleur est épuisée
                if est_epuisee:
                    overlay = pygame.Surface((rect.width, rect.height))
                    overlay.fill((128, 128, 128))
                    overlay.set_alpha(128)
                    self.ecran.blit(overlay, rect)
                
                # Contour blanc pour tous les boutons de couleur
                pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
                
                # Ajouter la flèche de sélection
                if couleur == self.couleur_selectionnee:
                    triangle_size = int(30 * min(self.RATIO_X, self.RATIO_Y))
                    triangle_x = rect.x - triangle_size - 10
                    triangle_y = rect.centery
                    points = [
                        (triangle_x, triangle_y - triangle_size//2),
                        (triangle_x, triangle_y + triangle_size//2),
                        (triangle_x + triangle_size, triangle_y)
                    ]
                    pygame.draw.polygon(self.ecran, self.BLANC, points)
                    pygame.draw.rect(self.ecran, self.BLANC, rect, 4)  # Contour plus épais pour la sélection
            
            else:  # Pour les autres boutons (save, load, clear)
                pygame.draw.rect(self.ecran, self.NOIR, rect, border_radius=20)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 2, border_radius=20)
                if "texte" in info_bouton:
                    texte = police_bouton.render(info_bouton["texte"], True, self.BLANC)
                    rect_texte = texte.get_rect(center=rect.center)
                    self.ecran.blit(texte, rect_texte)        # Bouton retour (identique à settings.py)
        pygame.draw.rect(self.ecran, self.bouton_retour["couleur"], self.bouton_retour["rect"], border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour["rect"], 2, border_radius=15)        
        police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        texte_retour = police_retour.render(self.bouton_retour["texte"], True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
        self.ecran.blit(texte_retour, rect_texte_retour)
          # Afficher le message d'erreur persistant si actif
        if self.message_erreur_actif and self.message_erreur:
            police_erreur = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
            texte_erreur = police_erreur.render(self.message_erreur, True, self.ROUGE)
            rect_erreur = texte_erreur.get_rect(center=(self.LARGEUR//2, 50))
            self.ecran.blit(texte_erreur, rect_erreur)
        
        # Afficher le message de succès persistant si actif
        if self.message_succes_actif and self.message_succes:
            police_succes = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
            texte_succes = police_succes.render(self.message_succes, True, self.VERT)
            rect_succes = texte_succes.get_rect(center=(self.LARGEUR//2, 100))
            self.ecran.blit(texte_succes, rect_succes)
        
        # Rien ici - suppression de l'affichage des couleurs en haut à droite

    def compter_couleurs(self):
        """Compte le nombre de carrés de chaque couleur dans le plateau."""
        comptes = {
            str(self.ROUGE): 0,
            str(self.VERT): 0,
            str(self.BLEU): 0,
            str(self.JAUNE): 0
        }
        for i in range(len(self.plateau)):
            for j in range(len(self.plateau[i])):
                couleur = str(self.plateau[i][j])
                if couleur in comptes:
                    comptes[couleur] += 1
        return comptes

    def obtenir_prochaine_couleur_disponible(self):
        """Retourne la prochaine couleur qui n'a pas encore 4 tuiles."""
        comptes = self.compter_couleurs()
        
        # Ordre de priorité pour les couleurs
        ordre_couleurs = [self.ROUGE, self.BLEU, self.JAUNE, self.VERT]
        
        for couleur in ordre_couleurs:
            if comptes[str(couleur)] < 4:
                return couleur
        
        # Si toutes les couleurs ont 4 tuiles, retourner la couleur actuelle
        return self.couleur_selectionnee

    def sauvegarder_plateau(self):
        """Sauvegarde le plateau actuel si la validation des couleurs est correcte."""
        comptes = self.compter_couleurs()
        
        # Vérifier que chaque couleur est utilisée exactement 4 fois
        for couleur, compte in comptes.items():
            if compte != 4:
                # Activer le message d'erreur persistant
                self.message_erreur = "Le plateau doit avoir exactement 4 carrés de chaque couleur!"
                self.message_erreur_actif = True
                return False  # La sauvegarde a échoué
          # Si on arrive ici, la sauvegarde est valide - désactiver le message d'erreur
        self.message_erreur_actif = False
        self.message_erreur = None
        
        # Désactiver tout message de succès précédent
        self.message_succes_actif = False
        self.message_succes = None
        
        # Créer une représentation du plateau avec les chemins d'images
        plateau_images = []
        for ligne in self.plateau:
            ligne_images = []
            for couleur in ligne:
                if couleur == self.ROUGE:
                    chemin = "assets/image_rouge.png"
                elif couleur == self.BLEU:
                    chemin = "assets/image_bleue.png"
                elif couleur == self.JAUNE:
                    chemin = "assets/image_jaune.png"
                elif couleur == self.VERT:
                    chemin = "assets/image_verte.png"
                else:
                    chemin = None
                ligne_images.append(chemin)
            plateau_images.append(ligne_images)
          # Sauvegarder le plateau
        if not os.path.exists("plateaux"):
            os.makedirs("plateaux")
        
        # Trouver le prochain numéro disponible
        fichiers_existants = [f for f in os.listdir("plateaux") if f.startswith("plateau_") and f.endswith(".json")]
        numeros_utilises = []
        for fichier in fichiers_existants:
            try:
                # Extraire le numéro du nom de fichier
                if fichier != "plateau_finale.json":
                    numero = int(fichier.replace("plateau_", "").replace(".json", ""))
                    numeros_utilises.append(numero)
            except ValueError:
                continue
        
        # Trouver le plus petit numéro disponible
        numero = 0
        while numero in numeros_utilises:
            numero += 1
            
        nouveau_nom = f"plateau_{numero}.json"
        chemin = os.path.join("plateaux", nouveau_nom)
        with open(chemin, "w") as f:
            json.dump(plateau_images, f)
          # Mettre à jour la liste des plateaux
        self.plateaux_sauvegardes.append(nouveau_nom)
        self.charger_liste_plateaux()  # Rafraîchir la liste
        
        # Afficher le message de succès
        self.message_succes = f"Plateau sauvegardé avec succès sous le nom {nouveau_nom}!"
        self.message_succes_actif = True
        
        return True  # La sauvegarde a réussi

    def charger_plateau(self, nom_fichier):
        """Charge un plateau depuis un fichier."""
        try:
            # Dictionnaire pour convertir les chemins d'images en couleurs
            image_vers_couleur = {
                "assets/image_rouge.png": self.ROUGE,
                "assets/image_bleue.png": self.BLEU,
                "assets/image_jaune.png": self.JAUNE,
                "assets/image_verte.png": self.VERT            }
            
            with open(f"plateaux/{nom_fichier}", 'r') as f:
                plateau_images = json.load(f)
                
                # Vérifier que le plateau chargé a la bonne taille
                if (len(plateau_images) != self.TAILLE_PLATEAU or 
                    any(len(ligne) != self.TAILLE_PLATEAU for ligne in plateau_images)):
                    raise ValueError("Taille de plateau invalide")
                
                # Convertir les chemins d'images en couleurs
                self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                              for _ in range(self.TAILLE_PLATEAU)]
                
                for i in range(self.TAILLE_PLATEAU):
                    for j in range(self.TAILLE_PLATEAU):
                        chemin = plateau_images[i][j]
                        if chemin in image_vers_couleur:
                            self.plateau[i][j] = image_vers_couleur[chemin]
            
            # Sauvegarder le nom du fichier chargé
            self.fichier_charge = nom_fichier
            
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            # Réinitialiser le plateau en cas d'erreur
            self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                          for _ in range(self.TAILLE_PLATEAU)]

    def supprimer_plateau(self, nom_fichier):
        try:
            chemin_fichier = os.path.join("plateaux", nom_fichier)
            if os.path.exists(chemin_fichier):
                os.remove(chemin_fichier)
                self.charger_liste_plateaux()
                # Ajuster la page courante si nécessaire
                max_pages = (len(self.plateaux_sauvegardes) + 7) // 8
                if self.page_courante >= max_pages:
                    self.page_courante = max(0, max_pages - 1)
        except Exception as e:
            print(f"Erreur lors de la suppression du plateau: {e}")

    def supprimer_plateaux_selectionnes(self):
        """Supprime tous les plateaux sélectionnés."""
        for index in sorted(self.plateaux_selectionnes, reverse=True):
            if index < len(self.plateaux_sauvegardes):
                nom_fichier = self.plateaux_sauvegardes[index]
                if nom_fichier != "plateau_finale.json":
                    try:
                        chemin_fichier = os.path.join("plateaux", nom_fichier)
                        if os.path.exists(chemin_fichier):
                            os.remove(chemin_fichier)
                    except Exception as e:
                        print(f"Erreur lors de la suppression du plateau {nom_fichier}: {e}")
          # Rafraîchir la liste et réinitialiser la sélection
        self.charger_liste_plateaux()
        self.plateaux_selectionnes.clear()
        self.mode_suppression = False
        
        # Ajuster la page courante si nécessaire
        if self.page_courante >= self.nombre_pages and self.nombre_pages > 0:
            self.page_courante = self.nombre_pages - 1

    def gerer_clic(self, pos):
        """Gère les clics sur l'éditeur."""
        x, y = pos
        
        # Gérer les clics sur les boutons de couleur
        for i, couleur in enumerate([self.ROUGE, self.VERT, self.BLEU, self.JAUNE]):
            bouton = pygame.Rect(self.largeur - 60, 100 + i * 70, 40, 40)
            if bouton.collidepoint(x, y):
                # Vérifier si la couleur n'a pas déjà été utilisée 4 fois
                comptes = self.compter_couleurs()
                if comptes[str(couleur)] < 4 or self.couleur_selectionnee == couleur:
                    self.couleur_selectionnee = couleur
                return True
        
        # ...existing code...

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
                            
                            # Placer la tuile
                            self.plateau[ligne][colonne] = self.couleur_selectionnee
                              # Désactiver le message d'erreur quand une tuile est changée
                            self.message_erreur_actif = False
                            self.message_erreur = None
                            
                            # Désactiver le message de succès quand une tuile est changée
                            self.message_succes_actif = False
                            self.message_succes = None
                              # Vérifier si la couleur actuelle a maintenant 4 tuiles
                            comptes = self.compter_couleurs()
                            if comptes[str(self.couleur_selectionnee)] >= 4:
                                # Changer automatiquement vers la prochaine couleur disponible
                                self.couleur_selectionnee = self.obtenir_prochaine_couleur_disponible()
                        
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
                                    # Réinitialiser le message d'erreur quand le plateau est effacé
                                    self.message_erreur_actif = False
                                    self.message_erreur = None
                                    # Réinitialiser le message de succès quand le plateau est effacé
                                    self.message_succes_actif = False
                                    self.message_succes = None
                    
                    elif self.mode == "selection":
                        # Vérifier le bouton retour
                        retour_rect = pygame.Rect(
                            int(50 * self.RATIO_X),
                            int(50 * self.RATIO_Y),
                            120, 40
                        )
                        # Vérifier le bouton nouveau
                        nouveau_rect = pygame.Rect(
                            self.LARGEUR - int(250 * self.RATIO_X),
                            int(50 * self.RATIO_Y),
                            int(200 * self.RATIO_X),
                            int(50 * self.RATIO_Y)
                        )

                        # Vérifier le bouton supprimer
                        supprimer_rect = pygame.Rect(
                            self.LARGEUR - int(500 * self.RATIO_X),
                            int(50 * self.RATIO_Y),
                            int(200 * self.RATIO_X),
                            int(50 * self.RATIO_Y)
                        )
                        
                        confirmer_rect = None
                        if self.mode_suppression and self.plateaux_selectionnes:
                            confirmer_rect = pygame.Rect(
                                self.LARGEUR//2 - int(200 * self.RATIO_X),
                                self.HAUTEUR - int(100 * self.RATIO_Y),
                                int(400 * self.RATIO_X),
                                int(50 * self.RATIO_Y)
                            )

                        if retour_rect.collidepoint(x, y):
                            self.mode = "editeur"
                            self.mode_suppression = False
                            self.plateaux_selectionnes.clear()
                        elif nouveau_rect.collidepoint(x, y):
                            self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                                        for _ in range(self.TAILLE_PLATEAU)]
                            if hasattr(self, 'fichier_charge'):
                                delattr(self, 'fichier_charge')
                            self.mode = "editeur"
                        elif supprimer_rect.collidepoint(x, y):
                            self.mode_suppression = not self.mode_suppression
                            self.plateaux_selectionnes.clear()
                        elif confirmer_rect and confirmer_rect.collidepoint(x, y):
                            self.supprimer_plateaux_selectionnes()
                        else:
                            # Vérifier les clics sur les boutons de navigation
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
                                elif suiv_rect.collidepoint(x, y) and self.page_courante < self.nombre_pages - 1:
                                    self.page_courante += 1
                                else:
                                    # Vérifier les clics sur les plateaux
                                    for idx, rect in enumerate(self.boutons_plateaux):
                                        if rect.collidepoint(x, y):
                                            index_reel = self.page_courante * 8 + idx
                                            if index_reel < len(self.plateaux_sauvegardes):
                                                if self.mode_suppression:
                                                    if self.plateaux_sauvegardes[index_reel] != "plateau_finale.json":
                                                        if index_reel in self.plateaux_selectionnes:
                                                            self.plateaux_selectionnes.remove(index_reel)
                                                        else:
                                                            self.plateaux_selectionnes.add(index_reel)
                                                else:
                                                    self.charger_plateau(self.plateaux_sauvegardes[index_reel])
                                                    self.mode = "editeur"
                                            break
                            else:
                                # Vérifier les clics sur les plateaux (sans navigation)
                                for idx, rect in enumerate(self.boutons_plateaux):
                                    if rect.collidepoint(x, y):
                                        index_reel = self.page_courante * 8 + idx
                                        if index_reel < len(self.plateaux_sauvegardes):
                                            if self.mode_suppression:
                                                if self.plateaux_sauvegardes[index_reel] != "plateau_finale.json":
                                                    if index_reel in self.plateaux_selectionnes:
                                                        self.plateaux_selectionnes.remove(index_reel)
                                                    else:
                                                        self.plateaux_selectionnes.add(index_reel)
                                            else:
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
