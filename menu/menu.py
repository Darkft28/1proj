import pygame
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

class Menu:
    def __init__(self):
        pygame.init()
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        
        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # Initialisation de l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Menu Principal")
        
        # Créer les boutons
        self.boutons = self._creer_boutons()
        
    def _creer_boutons(self):
        boutons = {}
        
        # Position centrale pour les boutons
        x_centre = self.LARGEUR // 2 - self.LARGEUR_BOUTON // 2
        y_debut = self.HAUTEUR // 2 - (3 * self.HAUTEUR_BOUTON + 2 * self.ESPACE_BOUTONS) // 2
        
        boutons_config = [
            ("jouer", self.VERT, "Jouer"),
            ("editeur", self.BLEU, "Créer votre quadrant"),
            ("parametres", self.JAUNE, "Paramètres")
        ]
        
        for i, (nom, couleur, texte) in enumerate(boutons_config):
            y = y_debut + i * (self.HAUTEUR_BOUTON + self.ESPACE_BOUTONS)
            boutons[nom] = {
                "rect": pygame.Rect(x_centre, y, self.LARGEUR_BOUTON, self.HAUTEUR_BOUTON),
                "couleur": couleur,
                "texte": texte
            }
        
        return boutons
    
    def dessiner(self):
        # Fond noir
        self.ecran.fill(self.NOIR)
        
        # Titre
        police_titre = pygame.font.Font(None, int(72 * min(self.RATIO_X, self.RATIO_Y)))
        titre = police_titre.render("1Proj", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, int(200 * self.RATIO_Y)))
        self.ecran.blit(titre, rect_titre)
        
        # Dessiner les boutons
        police = pygame.font.Font(None, int(48 * min(self.RATIO_X, self.RATIO_Y)))
        for info_bouton in self.boutons.values():
            # Dessiner le fond du bouton
            pygame.draw.rect(self.ecran, info_bouton["couleur"], info_bouton["rect"])
            pygame.draw.rect(self.ecran, self.BLANC, info_bouton["rect"], 2)
            
            # Dessiner le texte
            texte = police.render(info_bouton["texte"], True, self.BLANC)
            rect_texte = texte.get_rect(center=info_bouton["rect"].center)
            self.ecran.blit(texte, rect_texte)
    
    def executer(self):
        en_cours = True
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    for nom, info in self.boutons.items():
                        if info["rect"].collidepoint(x, y):
                            if nom == "editeur":
                                # Import modifié pour utiliser le chemin correct
                                from Board.editeur_board import EditeurPlateau4x4
                                editeur = EditeurPlateau4x4()
                                editeur.executer()
                                self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
                                pygame.display.set_caption("Menu Principal")
                            elif nom == "jouer":
                                print("Lancer le jeu")
                                from menu.play import Play
                                start = Play()
                                start.executer()
                                self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
                                pygame.display.set_caption("Choix du mode de jeu")
                            elif nom == "parametres":
                                print("Ouvrir les paramètres")
                                from menu.settings import Settings
                                settings = Settings(self.LARGEUR, self.HAUTEUR)
                                settings.executer()
                                nouvelle_largeur, nouvelle_hauteur = settings.get_resolution()
                                self.LARGEUR = nouvelle_largeur
                                self.HAUTEUR = nouvelle_hauteur
                                self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
                                pygame.display.set_caption("Paramètres")
            
            self.dessiner()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = Menu()
    menu.executer()