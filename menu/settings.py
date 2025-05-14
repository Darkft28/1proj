import pygame

class Settings:
    def __init__(self, largeur=None, hauteur=None):
        pygame.init()
        
        self.font_path = pygame.font.match_font('assets/police-gloomie_saturday/Gloomie Saturday.otf')
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = largeur if largeur is not None else info.current_w
        self.HAUTEUR = hauteur if hauteur is not None else info.current_h
        
        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440
        
        # Charger l'image d'arrière-plan
        self.background_image = pygame.image.load("assets/fond-menu-defaut.png")  # Remplacez par le chemin de votre image
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        self.GRIS = (150, 150, 150)
        self.GRIS_FONCE = (80, 80, 80)
        
        # Configuration des éléments d'interface
        self.LARGEUR_DROPDOWN = 700
        self.HAUTEUR_DROPDOWN = 90
        self.ESPACE_SECTIONS = 150
        
        # Initialisation de l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Paramètres")
        
        # Options disponibles pour chaque menu déroulant
        self.options_resolution = ["720p", "1080p", "1440p","1600p", "2160p"]
        self.options_theme = ["Clair", "Sombre", "Bleu", "Rouge"]
        self.options_langue = ["Francais", "English", "Español", "Deutsch"]
        
        # Options sélectionnées
        self.selected_resolution = 1  # Index par défaut (1080p)
        self.selected_theme = 0       # Index par défaut (Clair)
        self.selected_langue = 0      # Index par défaut (Français)
        
        # État des menus déroulants (ouvert/fermé)
        self.dropdown_resolution_ouvert = False
        self.dropdown_theme_ouvert = False
        self.dropdown_langue_ouvert = False
        
        
        # Créer les dropdowns
        self.dropdowns = self._creer_dropdowns()
        
        # Bouton retour
        self.bouton_retour = {
            "rect": pygame.Rect(int(50 * self.RATIO_X), int(50 * self.RATIO_Y), 
                            120, 40),  # Largeur 120px, hauteur 40px (plus petit)
            "couleur": self.ROUGE,
            "texte": "Retour"
        }
    
    def _creer_dropdowns(self):
        """Crée les menus déroulants pour les paramètres"""
        # Calculer les positions verticales pour chaque section
        y_resolution = int(600 * self.RATIO_Y)
        y_theme = y_resolution + self.ESPACE_SECTIONS
        y_langue = y_theme + self.ESPACE_SECTIONS

        # Position horizontale centrée pour les menus déroulants
        x_dropdown = (self.LARGEUR - self.LARGEUR_DROPDOWN) // 2

        # Créer un dictionnaire pour stocker les informations des menus déroulants
        dropdowns = {
            "resolution": {
                "titre": "Resolution",
                "dropdown_rect": pygame.Rect(x_dropdown, y_resolution, self.LARGEUR_DROPDOWN, self.HAUTEUR_DROPDOWN),
                "options": self.options_resolution,
                "selected": self.selected_resolution,
                "ouvert": self.dropdown_resolution_ouvert,
                "options_rects": []
            },
            "theme": {
                "titre": "Theme",
                "dropdown_rect": pygame.Rect(x_dropdown, y_theme, self.LARGEUR_DROPDOWN, self.HAUTEUR_DROPDOWN),
                "options": self.options_theme,
                "selected": self.selected_theme,
                "ouvert": self.dropdown_theme_ouvert,
                "options_rects": []
            },
            "langue": {
                "titre": "Langue",
                "dropdown_rect": pygame.Rect(x_dropdown, y_langue, self.LARGEUR_DROPDOWN, self.HAUTEUR_DROPDOWN),
                "options": self.options_langue,
                "selected": self.selected_langue,
                "ouvert": self.dropdown_langue_ouvert,
                "options_rects": []
            }
        }

        return dropdowns


    def dessiner(self):
        # Afficher l'image d'arrière-plan
        self.ecran.blit(self.background_image, (0, 0))
        
        # Police personnalisée pour tous les textes
        police_titre = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 72)
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 48)
        
        # Titre principal
        titre = police_titre.render("PARAMETRES :", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR // 2, int(450 * self.RATIO_Y)))
        self.ecran.blit(titre, rect_titre)
        
        # Dessiner les sections et menus déroulants fermés
        menus_ouverts = []
        for nom, info in self.dropdowns.items():
            if nom == "resolution":
                # Affiche la résolution actuelle
                texte_bouton = f"{info['titre']} : {self.LARGEUR} x {self.HAUTEUR}"
            else:
                texte_bouton = f"{info['titre']} : {info['options'][info['selected']]}"
            texte_rendu = police_bouton.render(texte_bouton, True, self.BLANC)
            
            rect_bouton = info["dropdown_rect"]
            pygame.draw.rect(self.ecran, self.GRIS_FONCE, rect_bouton, border_radius=15)
            pygame.draw.rect(self.ecran, self.BLANC, rect_bouton, 2, border_radius=15)
            
            rect_texte = texte_rendu.get_rect(center=rect_bouton.center)
            self.ecran.blit(texte_rendu, rect_texte)
            
            arrow_points = [
                (rect_bouton.right - int(30 * self.RATIO_X), rect_bouton.centery - int(10 * self.RATIO_Y)),
                (rect_bouton.right - int(15 * self.RATIO_X), rect_bouton.centery + int(10 * self.RATIO_Y)),
                (rect_bouton.right - int(45 * self.RATIO_X), rect_bouton.centery + int(10 * self.RATIO_Y))
            ]
            pygame.draw.polygon(self.ecran, self.BLANC, arrow_points)
            
            if info["ouvert"]:
                menus_ouverts.append(info)
        
        # Bouton retour
        pygame.draw.rect(self.ecran, self.bouton_retour["couleur"], self.bouton_retour["rect"], border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour["rect"], 2, border_radius=15)
        
        police_retour = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 28)
        texte_retour = police_retour.render(self.bouton_retour["texte"], True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
        self.ecran.blit(texte_retour, rect_texte_retour)
        
        
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
        self.ecran.blit(texte_retour, rect_texte_retour)
        
        # Dessiner les menus déroulants ouverts en dernier
        for info in menus_ouverts:
            self._dessiner_menu_ouvert(info)

    def _dessiner_menu_ouvert(self, info):
        """Dessiner les options d'un menu déroulant ouvert."""
        menu_height = len(info["options_rects"]) * self.HAUTEUR_DROPDOWN
        menu_width = info["dropdown_rect"].width
        
        fond_rect = pygame.Rect(
            info["dropdown_rect"].x,
            info["dropdown_rect"].bottom,
            menu_width,
            menu_height
        )
        pygame.draw.rect(self.ecran, self.GRIS_FONCE, fond_rect, border_radius=15)

        # Police personnalisée pour les options
        police_options = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 42)
        
        for i, option_rect in enumerate(info["options_rects"]):
            couleur_fond = self.VERT if i == info["selected"] else self.GRIS
            pygame.draw.rect(self.ecran, couleur_fond, option_rect, border_radius=10)
            pygame.draw.rect(self.ecran, self.BLANC, option_rect, 2, border_radius=10)
            
            texte_option = police_options.render(info["options"][i], True, self.BLANC)
            rect_texte = texte_option.get_rect(
                midleft=(option_rect.x + int(20 * self.RATIO_X), option_rect.centery)
            )
            self.ecran.blit(texte_option, rect_texte)


    def _dessiner_menu_ouvert(self, info):
        """Dessiner les options d'un menu déroulant ouvert."""
        menu_height = len(info["options_rects"]) * self.HAUTEUR_DROPDOWN
        menu_width = info["dropdown_rect"].width
        
        # Dessiner un fond opaque pour les options
        fond_rect = pygame.Rect(
            info["dropdown_rect"].x,
            info["dropdown_rect"].bottom,
            menu_width,
            menu_height
        )
        pygame.draw.rect(self.ecran, self.GRIS_FONCE, fond_rect, border_radius=15)  # Fond gris foncé avec bords arrondis

        # Police pour les options
        police_options = pygame.font.Font(None, int(42 * min(self.RATIO_X, self.RATIO_Y)))
        
        # Dessiner chaque option
        for i, option_rect in enumerate(info["options_rects"]):
            # Fond de l'option
            couleur_fond = self.VERT if i == info["selected"] else self.GRIS
            pygame.draw.rect(self.ecran, couleur_fond, option_rect, border_radius=10)
            pygame.draw.rect(self.ecran, self.BLANC, option_rect, 2, border_radius=10)  # Bordure blanche
            
            # Texte de l'option
            texte_option = police_options.render(info["options"][i], True, self.BLANC)  # Texte blanc
            rect_texte = texte_option.get_rect(
                midleft=(option_rect.x + int(20 * self.RATIO_X), option_rect.centery)
            )
            self.ecran.blit(texte_option, rect_texte)


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
                    
                    # Vérifier les clics sur les menus déroulants
                    dropdown_clique = False
                    for nom, info in self.dropdowns.items():
                        # Clic sur le menu déroulant principal
                        if info["dropdown_rect"].collidepoint(x, y):
                            dropdown_clique = True
                            # Fermer tous les autres menus déroulants
                            for autre_nom in self.dropdowns:
                                if autre_nom != nom:
                                    self.dropdowns[autre_nom]["ouvert"] = False
                            
                            # Inverser l'état du menu actuel
                            info["ouvert"] = not info["ouvert"]
                            
                            # Recréer les rectangles pour les options si le menu est ouvert
                            if info["ouvert"]:
                                info["options_rects"] = []
                                x_dropdown = (self.LARGEUR - self.LARGEUR_DROPDOWN) // 2  # <-- Ajoute cette ligne ici
                                for j in range(len(info["options"])):
                                    option_rect = pygame.Rect(
                                        x_dropdown,  # <-- Utilise x_dropdown ici
                                        info["dropdown_rect"].bottom + j * self.HAUTEUR_DROPDOWN,
                                        self.LARGEUR_DROPDOWN,
                                        self.HAUTEUR_DROPDOWN
                                    )
                                    info["options_rects"].append(option_rect)
                        
                        # Si le menu est ouvert, vérifier les clics sur les options
                        elif info["ouvert"]:
                            for i, option_rect in enumerate(info["options_rects"]):
                                if i < len(info["options"]) and option_rect.collidepoint(x, y):
                                    dropdown_clique = True
                                    info["selected"] = i
                                    info["ouvert"] = False
                                    
                                    # Appliquer les changements de paramètres
                                    if nom == "resolution":
                                        print(f"Résolution {info['options'][i]} sélectionnée")
                                        self._changer_resolution(info['options'][i])
                                    elif nom == "theme":
                                        print(f"Thème {info['options'][i]} sélectionné")
                                        # TODO: Appliquer le changement de thème
                                    elif nom == "langue":
                                        print(f"Langue {info['options'][i]} sélectionnée")
                                        # TODO: Appliquer le changement de langue
                    
                    # Si on a cliqué en dehors des menus déroulants, tous les fermer
                    if not dropdown_clique:
                        for nom in self.dropdowns:
                            self.dropdowns[nom]["ouvert"] = False
            
            self.dessiner()
            pygame.display.flip()
        
        # Retourne au menu principal sans quitter le jeu

    def _changer_resolution(self, resolution):
        resolutions_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "1440p": (2560, 1440),
            "1600p": (2560, 1600),
            "2160p": (3840, 2160)
        }
        if resolution in resolutions_map:
            largeur, hauteur = resolutions_map[resolution]
            self.LARGEUR = largeur
            self.HAUTEUR = hauteur
            self.RATIO_X = self.LARGEUR / 2560
            self.RATIO_Y = self.HAUTEUR / 1440

            # Mettre à jour l'écran avec la nouvelle résolution
            self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))


            # Recréer les dropdowns avec les nouvelles dimensions d'écran
            self.dropdowns = self._creer_dropdowns()
            print(f"Résolution changée à {largeur}x{hauteur}")

            # Mettre à jour l'option sélectionnée dans le menu déroulant
            self.dropdowns["resolution"]["selected"] = self.options_resolution.index(resolution)

    def get_resolution(self):
        return self.LARGEUR, self.HAUTEUR


if __name__ == "__main__":
    settings = Settings()
    settings.executer()