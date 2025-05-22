import pygame

class MenuMode:
    def __init__(self, largeur, hauteur):
        self.LARGEUR = largeur
        self.HAUTEUR = hauteur
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.background_image = pygame.image.load("assets/menu-claire/fond-menu-principal.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        
                # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440
        
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        self.boutons = self._creer_boutons()
        
        
        self.bouton_retour = {
            "rect": pygame.Rect(int(50 * self.RATIO_X), int(50 * self.RATIO_Y), 120, 40),  # même taille que settings.py
            "couleur": self.ROUGE,
            "texte": "Retour"
        }

    def _creer_boutons(self):
        boutons = {}
        noms = [("local", "Joueur vs Joueur"), ("ia", "Joueur vs IA"), ("online", "En ligne")]
        largeur_bouton = 400
        hauteur_bouton = 80
        espace = 40
        x = self.LARGEUR // 2 - largeur_bouton // 2
        total_height = len(noms) * hauteur_bouton + (len(noms) - 1) * espace
        y_debut = self.HAUTEUR // 2 - total_height // 2
        for i, (nom, texte) in enumerate(noms):
            y = y_debut + i * (hauteur_bouton + espace)
            boutons[nom] = {
                "rect": pygame.Rect(x, y, largeur_bouton, hauteur_bouton),
                "texte": texte
            }
        return boutons

    def afficher(self):
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        en_cours = True
        choix = None
        while en_cours:
            self.ecran.blit(self.background_image, (0, 0))
            titre = police.render("Choisissez le mode de jeu", True, self.BLANC)
            rect_titre = titre.get_rect(center=(self.LARGEUR // 2, 150))
            self.ecran.blit(titre, rect_titre)
            for nom, info in self.boutons.items():
                pygame.draw.rect(self.ecran, self.NOIR, info["rect"], border_radius=30)
                pygame.draw.rect(self.ecran, self.BLANC, info["rect"], 3, border_radius=30)
                texte = police_bouton.render(info["texte"], True, self.BLANC)
                rect_texte = texte.get_rect(center=info["rect"].center)
                self.ecran.blit(texte, rect_texte)
            # Bouton retour
            pygame.draw.rect(self.ecran, self.bouton_retour["couleur"], self.bouton_retour["rect"], border_radius=15)
            pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour["rect"], 2, border_radius=15)
            police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
            texte_retour = police_retour.render(self.bouton_retour["texte"], True, self.BLANC)
            rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
            self.ecran.blit(texte_retour, rect_texte_retour)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # Bouton retour
                    if self.bouton_retour["rect"].collidepoint(x, y):
                        choix = None
                        en_cours = False
                    for nom, info in self.boutons.items():
                        if info["rect"].collidepoint(x, y):
                            choix = nom
                            en_cours = False
        return choix