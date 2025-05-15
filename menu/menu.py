import pygame
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

class Menu:
    def __init__(self):
        pygame.init()
        
        self.font_path = pygame.font.match_font('assets/police-gloomie_saturday/Gloomie Saturday.otf')
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        
        # Fond d'écran
        self.background_image = pygame.image.load("assets/menu-claire/fond-menu-principal.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        
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

        # Taille fixe pour les boutons
        self.LARGEUR_BOUTON = 400
        self.HAUTEUR_BOUTON = 80
        self.ESPACE_BOUTONS = 40

        boutons_config = [
            ("jouer", self.NOIR, "Jouer"),
            ("editeur", self.NOIR, "Creer votre quadrant"),
            ("parametres", self.NOIR, "Parametres")
        ]

        nb_boutons = len(boutons_config)
        total_height = nb_boutons * self.HAUTEUR_BOUTON + (nb_boutons - 1) * self.ESPACE_BOUTONS

        # Calcul du centre horizontal et vertical à CHAQUE appel
        x_centre = self.LARGEUR // 2 - self.LARGEUR_BOUTON // 2
        y_debut = self.HAUTEUR // 2 - total_height // 2

        for i, (nom, couleur, texte) in enumerate(boutons_config):
            y = y_debut + i * (self.HAUTEUR_BOUTON + self.ESPACE_BOUTONS)
            boutons[nom] = {
                "rect": pygame.Rect(x_centre, y, self.LARGEUR_BOUTON, self.HAUTEUR_BOUTON),
                "couleur": couleur,
                "texte": texte
            }

        return boutons

    def dessiner(self):
        # Afficher l'image d'arrière-plan
        self.ecran.blit(self.background_image, (0, 0))
        
        # Police personnalisée pour tous les textes
        police_titre = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 48)
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
        
        # Titre
        titre = police_titre.render("KATARENGA & Co", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, 200))
        self.ecran.blit(titre, rect_titre)
        
        # Dessiner les boutons noirs et arrondis
        for info_bouton in self.boutons.values():
            pygame.draw.rect(self.ecran, info_bouton["couleur"], info_bouton["rect"], border_radius=30)
            pygame.draw.rect(self.ecran, self.BLANC, info_bouton["rect"], 3, border_radius=30)
            texte = police_bouton.render(info_bouton["texte"], True, self.BLANC)
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
                                self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
                                pygame.display.set_caption("Menu Principal")
                                self.boutons = self._creer_boutons()  # Pour bien recentrer les boutons si besoin
            
            self.dessiner()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = Menu()
    menu.executer()