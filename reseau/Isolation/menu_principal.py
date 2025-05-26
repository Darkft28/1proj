import pygame
import sys
import subprocess
import os

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
        pygame.display.set_caption("Isolation - Menu Principal")
        
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
        try:
            self.background = pygame.image.load("assets/menu-claire/fond-menu-principal.png")
            self.background = pygame.transform.scale(self.background, (self.LARGEUR, self.HAUTEUR))
        except:
            self.background = None
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(100 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(50 * self.RATIO_Y)
        
        # Création des boutons
        self.creer_boutons()
        
    def creer_boutons(self):
        # Position centrale pour les boutons
        centre_x = self.LARGEUR // 2
        centre_y = self.HAUTEUR // 2
        
        # Bouton Host
        self.bouton_host = pygame.Rect(
            centre_x - self.LARGEUR_BOUTON // 2,
            centre_y - self.HAUTEUR_BOUTON - self.ESPACE_BOUTONS,
            self.LARGEUR_BOUTON,
            self.HAUTEUR_BOUTON
        )
        
        # Bouton Guest
        self.bouton_guest = pygame.Rect(
            centre_x - self.LARGEUR_BOUTON // 2,
            centre_y + self.ESPACE_BOUTONS,
            self.LARGEUR_BOUTON,
            self.HAUTEUR_BOUTON
        )
        
        # Bouton Quitter
        self.bouton_quitter = pygame.Rect(
            centre_x - self.LARGEUR_BOUTON // 2,
            centre_y + self.HAUTEUR_BOUTON + 2 * self.ESPACE_BOUTONS,
            self.LARGEUR_BOUTON,
            self.HAUTEUR_BOUTON
        )
    
    def dessiner_bouton(self, bouton, texte, couleur, survol=False):
        if survol:
            couleur_finale = tuple(min(c + 30, 255) for c in couleur)
        else:
            couleur_finale = couleur
            
        # Dessiner le bouton avec coins arrondis
        pygame.draw.rect(self.ecran, couleur_finale, bouton, border_radius=20)
        
        # Dessiner le texte
        surface_texte = self.police_bouton.render(texte, True, self.BLANC)
        rect_texte = surface_texte.get_rect(center=bouton.center)
        self.ecran.blit(surface_texte, rect_texte)
    
    def dessiner_interface(self):
        # Fond
        if self.background:
            self.ecran.blit(self.background, (0, 0))
        else:
            self.ecran.fill(self.BLANC)
        
        # Titre
        titre = "ISOLATION"
        surface_titre = self.police_titre.render(titre, True, self.NOIR)
        rect_titre = surface_titre.get_rect(center=(self.LARGEUR // 2, int(150 * self.RATIO_Y)))
        self.ecran.blit(surface_titre, rect_titre)
        
        # Sous-titre
        sous_titre = "Jeu de Blocage en Reseau"
        surface_sous_titre = self.police_info.render(sous_titre, True, self.NOIR)
        rect_sous_titre = surface_sous_titre.get_rect(center=(self.LARGEUR // 2, int(220 * self.RATIO_Y)))
        self.ecran.blit(surface_sous_titre, rect_sous_titre)
        
        # Position de la souris pour l'effet de survol
        pos_souris = pygame.mouse.get_pos()
        
        # Dessiner les boutons
        self.dessiner_bouton(
            self.bouton_host, 
            "Creer une partie", 
            self.BLEU,
            self.bouton_host.collidepoint(pos_souris)
        )
        
        self.dessiner_bouton(
            self.bouton_guest, 
            "Rejoindre une partie", 
            self.VERT,
            self.bouton_guest.collidepoint(pos_souris)
        )
        
        self.dessiner_bouton(
            self.bouton_quitter, 
            "Quitter", 
            self.ROUGE,
            self.bouton_quitter.collidepoint(pos_souris)
        )
        
        # Instructions
        instructions = [
            "Creez une partie pour devenir l'hote",
            "Rejoignez une partie existante en tant qu'invite"
        ]
        
        y_instructions = self.HAUTEUR - int(150 * self.RATIO_Y)
        for instruction in instructions:
            surface_instruction = self.police_info.render(instruction, True, self.NOIR)
            rect_instruction = surface_instruction.get_rect(center=(self.LARGEUR // 2, y_instructions))
            self.ecran.blit(surface_instruction, rect_instruction)
            y_instructions += int(40 * self.RATIO_Y)
    
    def lancer_host(self):
        """Lance le jeu en mode Host"""
        pygame.quit()
        # Lancer le fichier host
        subprocess.Popen([sys.executable, "reseau/plateau_pion_host.py"])
        sys.exit()
    
    def lancer_guest(self):
        """Lance le jeu en mode Guest"""
        pygame.quit()
        # Lancer le fichier guest
        subprocess.Popen([sys.executable, "reseau/plateau_pion_guest.py"])
        sys.exit()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        pos = pygame.mouse.get_pos()
                        
                        if self.bouton_host.collidepoint(pos):
                            self.lancer_host()
                        
                        elif self.bouton_guest.collidepoint(pos):
                            self.lancer_guest()
                        
                        elif self.bouton_quitter.collidepoint(pos):
                            running = False
            
            self.dessiner_interface()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = MenuPrincipal()
    menu.run()