import pygame
from menu.menu_mode import MenuMode 

class Play:
    def __init__(self):
        pygame.init()
        
        self.font_path = pygame.font.match_font('assets/police-gloomie_saturday/Gloomie Saturday.otf')
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        
        # Fond d'écran
        self.background_image = pygame.image.load("assets/menu-claire/fond-menu-jouer.png")
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
        pygame.display.set_caption("Choix du jeu")
        
        # Créer les boutons
        self.boutons = self._creer_boutons()
        
        # Bouton retour
        self.bouton_retour = {
            "rect": pygame.Rect(int(50 * self.RATIO_X), int(50 * self.RATIO_Y), 120, 40),  # même taille que settings.py
            "couleur": self.ROUGE,
            "texte": "Retour"
        }
        
    def _creer_boutons(self):
        boutons = {}

        # Taille fixe pour les boutons
        self.LARGEUR_BOUTON = 400
        self.HAUTEUR_BOUTON = 80
        self.ESPACE_BOUTONS = 40

        boutons_config = [
            ("Katarenga", self.NOIR, "Katarenga"),
            ("Isolation", self.NOIR, "Isolation"),
            ("Congress", self.NOIR, "Congress")
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
        titre = police_titre.render("Choix du jeu", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, 200))
        self.ecran.blit(titre, rect_titre)
        
        # Dessiner les boutons noirs, arrondis, contour blanc, texte centré
        for info_bouton in self.boutons.values():
            pygame.draw.rect(self.ecran, info_bouton["couleur"], info_bouton["rect"], border_radius=30)
            pygame.draw.rect(self.ecran, self.BLANC, info_bouton["rect"], 3, border_radius=30)
            texte = police_bouton.render(info_bouton["texte"], True, self.BLANC)
            rect_texte = texte.get_rect(center=info_bouton["rect"].center)
            self.ecran.blit(texte, rect_texte)
        
        # Dessiner le bouton retour (identique à settings.py)
        pygame.draw.rect(self.ecran, self.bouton_retour["couleur"], self.bouton_retour["rect"], border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour["rect"], 2, border_radius=15)
        police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        texte_retour = police_retour.render(self.bouton_retour["texte"], True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
        self.ecran.blit(texte_retour, rect_texte_retour)
    
    def executer(self):
        en_cours = True
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    # Vérifier le clic sur le bouton retour
                    if self.bouton_retour["rect"].collidepoint(x, y):
                        en_cours = False

                    # Vérifier les clics sur les boutons de jeux
                    for nom, info in self.boutons.items():
                        if info["rect"].collidepoint(x, y):
                            mode = MenuMode(self.LARGEUR, self.HAUTEUR).afficher()
                            print(f"Lancer {nom} en mode : {mode}")
                            # Ici, lance le jeu correspondant avec le mode choisi
                            break  # On sort de la boucle for pour éviter plusieurs actions

            self.dessiner()
            pygame.display.flip()
        
        # Retourne au menu principal sans quitter le jeu

if __name__ == "__main__":
    start = Play()
    start.executer()
