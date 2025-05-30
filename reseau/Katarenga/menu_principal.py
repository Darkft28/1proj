import pygame
import sys
import subprocess
import os
from menu.config import get_theme

# Répertoire du fichier en cours
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MenuPrincipal:
    def __init__(self):
        pygame.init()
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        
        # Calcul des ratios d'échelle
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440
        
        # Initialisation de la fenêtre
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Katarenga - Menu Principal")
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.VERT = (24, 181, 87)
        self.GRIS = (200, 200, 200)
        
        # Police
        try:
            self.font_path = 'assets/police-gloomie_saturday/Gloomie Saturday.otf'
            self.police_titre = pygame.font.Font(self.font_path, int(80 * self.RATIO_X))
            self.police_bouton = pygame.font.Font(self.font_path, int(40 * self.RATIO_X))
            self.police_info = pygame.font.Font(self.font_path, int(30 * self.RATIO_X))
        except:
            self.police_titre = pygame.font.Font(None, int(80 * self.RATIO_X))
            self.police_bouton = pygame.font.Font(None, int(40 * self.RATIO_X))
            self.police_info = pygame.font.Font(None, int(30 * self.RATIO_X))
        
        # Fond d'écran
        theme = get_theme()
        if theme == "Sombre":
            self.background_image = pygame.image.load("assets/menu/menu-sombre.png")
        else:
            self.background_image = pygame.image.load("assets/menu/menu-claire.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # Variables d'état
        self.running = True
        self.selection = 0  # 0: Héberger, 1: Rejoindre, 2: Retour
        
        # Configuration des boutons
        self.boutons = []
        self.creer_boutons()
    
    def creer_boutons(self):
        """Crée les boutons du menu"""
        centre_x = self.LARGEUR // 2
        centre_y = self.HAUTEUR // 2
        
        # Bouton Héberger
        self.bouton_heberger = pygame.Rect(
            centre_x - self.LARGEUR_BOUTON // 2,
            centre_y - self.HAUTEUR_BOUTON - self.ESPACE_BOUTONS,
            self.LARGEUR_BOUTON,
            self.HAUTEUR_BOUTON
        )
        
        # Bouton Rejoindre
        self.bouton_rejoindre = pygame.Rect(
            centre_x - self.LARGEUR_BOUTON // 2,
            centre_y,
            self.LARGEUR_BOUTON,
            self.HAUTEUR_BOUTON
        )
        
        # Bouton Retour
        self.bouton_retour = pygame.Rect(
            centre_x - self.LARGEUR_BOUTON // 2,
            centre_y + self.HAUTEUR_BOUTON + self.ESPACE_BOUTONS,
            self.LARGEUR_BOUTON,
            self.HAUTEUR_BOUTON
        )
        
        self.boutons = [self.bouton_heberger, self.bouton_rejoindre, self.bouton_retour]
    
    def dessiner_bouton(self, bouton, texte, selectionne=False):
        """Dessine un bouton avec le texte centré"""
        couleur = self.VERT if selectionne else self.BLEU
        pygame.draw.rect(self.ecran, couleur, bouton, border_radius=20)
        pygame.draw.rect(self.ecran, self.NOIR, bouton, 3, border_radius=20)
        
        surface_texte = self.police_bouton.render(texte, True, self.BLANC)
        rect_texte = surface_texte.get_rect(center=bouton.center)
        self.ecran.blit(surface_texte, rect_texte)
    
    def afficher_titre(self):
        """Affiche le titre du menu"""
        texte = "Katarenga - Mode En Ligne"
        surface_titre = self.police_titre.render(texte, True, self.BLANC)
        rect_titre = surface_titre.get_rect(center=(self.LARGEUR // 2, int(200 * self.RATIO_Y)))
        self.ecran.blit(surface_titre, rect_titre)
    
    def afficher_info(self):
        """Affiche les informations du menu"""
        infos = [
            "Héberger: Créer une partie et attendre un adversaire",
            "Rejoindre: Se connecter à une partie existante",
            "Utilisez les flèches pour naviguer, Entrée pour valider"
        ]
        
        y_start = int(self.HAUTEUR - 150 * self.RATIO_Y)
        for i, info in enumerate(infos):
            surface_info = self.police_info.render(info, True, self.BLANC)
            rect_info = surface_info.get_rect(center=(self.LARGEUR // 2, y_start + i * 40))
            self.ecran.blit(surface_info, rect_info)
    
    def gerer_evenements(self):
        """Gère les événements du menu"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selection = (self.selection - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.selection = (self.selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    self.executer_selection()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    for i, bouton in enumerate(self.boutons):
                        if bouton.collidepoint(event.pos):
                            self.selection = i
                            self.executer_selection()
                            break
            
            elif event.type == pygame.MOUSEMOTION:
                # Mettre à jour la sélection selon la position de la souris
                for i, bouton in enumerate(self.boutons):
                    if bouton.collidepoint(event.pos):
                        self.selection = i
                        break
    
    def executer_selection(self):
        """Exécute l'action correspondant à la sélection"""
        if self.selection == 0:  # Héberger
            self.heberger_partie()
        elif self.selection == 1:  # Rejoindre
            self.rejoindre_partie()
        elif self.selection == 2:  # Retour
            self.running = False
    
    def heberger_partie(self):
        """Lance le mode hébergeur"""
        try:
            # Importer et lancer le mode hébergeur
            from .plateau_pion_host import Plateau_pion_host
            host = Plateau_pion_host()
            host.run()
        except ImportError as e:
            print(f"Erreur lors de l'import du module host: {e}")
        except Exception as e:
            print(f"Erreur lors du lancement du mode hébergeur: {e}")
    
    def rejoindre_partie(self):
        """Lance le mode invité"""
        try:
            # Importer et lancer le mode invité
            from .plateau_pion_guest import Plateau_pion_guest
            guest = Plateau_pion_guest()
            guest.run()
        except ImportError as e:
            print(f"Erreur lors de l'import du module guest: {e}")
        except Exception as e:
            print(f"Erreur lors du lancement du mode invité: {e}")
    
    def run(self):
        """Boucle principale du menu"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Gestion des événements
            self.gerer_evenements()
            
            # Affichage
            self.ecran.blit(self.background_image, (0, 0))
            
            # Afficher le titre
            self.afficher_titre()
            
            # Afficher les boutons
            self.dessiner_bouton(self.bouton_heberger, "Héberger", self.selection == 0)
            self.dessiner_bouton(self.bouton_rejoindre, "Rejoindre", self.selection == 1)
            self.dessiner_bouton(self.bouton_retour, "Retour", self.selection == 2)
            
            # Afficher les informations
            self.afficher_info()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    menu = MenuPrincipal()
    menu.run()
