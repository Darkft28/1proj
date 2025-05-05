import pygame
import sys
import json
import os

class EditeurPlateau4x4:
    def __init__(self):
        pygame.init()
        
        # Dimensions de l'écran
        self.LARGEUR = 2560
        self.HAUTEUR = 1440
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        
        # Configuration du plateau
        self.TAILLE_PLATEAU = 4
        self.TAILLE_CASE = 280
        self.couleurs_disponibles = [self.ROUGE, self.BLEU, self.JAUNE, self.VERT]
        self.couleur_selectionnee = self.ROUGE
        
        # Initialisation de l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Éditeur de Plateau 4x4")
        
        # Création du plateau vide
        self.plateau = [[self.NOIR for _ in range(self.TAILLE_PLATEAU)] 
                       for _ in range(self.TAILLE_PLATEAU)]
        
        # Position du plateau
        self.plateau_x = 720
        self.plateau_y = 160
        
        # État de l'interface
        self.mode = "editeur"  # "editeur" ou "selection"
        self.plateaux_sauvegardes = []
        self.boutons_plateaux = []
        
        # Boutons
        self.boutons = self._creer_boutons()

    def _creer_boutons(self):
        boutons = {}
        x_couleur = 360
        y_couleur = 450
        
        # Boutons de couleurs
        for i, couleur in enumerate(self.couleurs_disponibles):
            boutons[f"couleur_{i}"] = {
                "rect": pygame.Rect(x_couleur, y_couleur + i*150, 140, 140),
                "couleur": couleur,
                "action": "select_color"
            }
        
        # Bouton Sauvegarder
        boutons["sauvegarder"] = {
            "rect": pygame.Rect(2088, 550, 225, 60),
            "couleur": self.VERT,
            "texte": "Sauvegarder",
            "action": "save"
        }
        
        # Bouton Charger
        boutons["charger"] = {
            "rect": pygame.Rect(2088, 690, 225, 60),
            "couleur": self.BLEU,
            "texte": "Charger",
            "action": "load"
        }
        
        # Bouton Effacer
        boutons["effacer"] = {
            "rect": pygame.Rect(2088, 830, 225, 60),
            "couleur": self.ROUGE,
            "texte": "Effacer tout",
            "action": "clear"
        }
        
        return boutons

    def charger_liste_plateaux(self):
        self.plateaux_sauvegardes = []
        self.boutons_plateaux = []
        y_pos = 100
        
        if not os.path.exists("plateaux"):
            os.makedirs("plateaux")
            
        for fichier in os.listdir("plateaux"):
            if fichier.endswith('.json'):
                rect = pygame.Rect(50, y_pos, 700, 60)
                self.plateaux_sauvegardes.append(fichier)
                self.boutons_plateaux.append(rect)
                y_pos += 80

    def dessiner_ecran_selection(self):
        self.ecran.fill(self.NOIR)
        
        # Titre
        police = pygame.font.Font(None, 48)
        titre = police.render("Sélectionnez un plateau", True, self.BLANC)
        self.ecran.blit(titre, (50, 30))

        # Dessiner les plateaux sauvegardés
        if not self.plateaux_sauvegardes:
            texte = police.render("Aucun plateau sauvegardé", True, self.BLANC)
            self.ecran.blit(texte, (50, 100))
        else:
            police = pygame.font.Font(None, 36)
            for idx, fichier in enumerate(self.plateaux_sauvegardes):
                rect = self.boutons_plateaux[idx]
                pygame.draw.rect(self.ecran, self.BLEU, rect)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 2)
                
                texte = police.render(fichier, True, self.BLANC)
                self.ecran.blit(texte, (rect.x + 20, rect.y + 20))

        # Bouton retour
        retour_rect = pygame.Rect(50, self.HAUTEUR - 70, 200, 50)
        pygame.draw.rect(self.ecran, self.ROUGE, retour_rect)
        pygame.draw.rect(self.ecran, self.BLANC, retour_rect, 2)
        police = pygame.font.Font(None, 36)
        texte = police.render("Retour", True, self.BLANC)
        self.ecran.blit(texte, (110, self.HAUTEUR - 55))
        
        return retour_rect

    def dessiner(self):
        self.ecran.fill(self.NOIR)
        
        # Dessiner le plateau
        for ligne in range(self.TAILLE_PLATEAU):
            for colonne in range(self.TAILLE_PLATEAU):
                x = self.plateau_x + colonne * self.TAILLE_CASE
                y = self.plateau_y + ligne * self.TAILLE_CASE
                
                rect = pygame.Rect(x, y, self.TAILLE_CASE, self.TAILLE_CASE)
                pygame.draw.rect(self.ecran, self.plateau[ligne][colonne], rect)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
        
        # Dessiner les boutons
        for info_bouton in self.boutons.values():
            pygame.draw.rect(self.ecran, info_bouton["couleur"], info_bouton["rect"])
            pygame.draw.rect(self.ecran, self.BLANC, info_bouton["rect"], 2)
            
            if "texte" in info_bouton:
                police = pygame.font.Font(None, 30)
                texte = police.render(info_bouton["texte"], True, self.BLANC)
                rect_texte = texte.get_rect(center=info_bouton["rect"].center)
                self.ecran.blit(texte, rect_texte)

    def sauvegarder_plateau(self):
        if not os.path.exists("plateaux"):
            os.makedirs("plateaux")
            
        try:
            num = len([f for f in os.listdir("plateaux") if f.endswith('.json')])
            nom_fichier = f"plateaux/plateau_{num}.json"
            with open(nom_fichier, 'w') as f:
                plateau_save = [[(c[0], c[1], c[2]) for c in ligne] 
                              for ligne in self.plateau]
                json.dump(plateau_save, f)
            print(f"Plateau sauvegardé sous {nom_fichier}!")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def charger_plateau(self, nom_fichier):
        try:
            with open(f"plateaux/{nom_fichier}", 'r') as f:
                plateau_load = json.load(f)
                self.plateau = [[tuple(c) for c in ligne] 
                              for ligne in plateau_load]
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
                        retour_rect = pygame.Rect(50, self.HAUTEUR - 70, 200, 50)
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