import pygame
import sys
import os

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class MenuMode:
    def __init__(self, jeu):
        pygame.init()
        self.jeu = jeu  # Stocke le jeu sélectionné depuis play.py

        # Résolution
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h

        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption(f"Choix du mode - {self.jeu}")

        self.font_path = 'assets/police-gloomie_saturday/Gloomie Saturday.otf'
        self.background_image = pygame.image.load("assets/menu-claire/fond-menu-jouer.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))

        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)

        self.boutons = self._creer_boutons()
        self.bouton_retour = {
            "rect": pygame.Rect(50, 50, 120, 40),
            "couleur": self.ROUGE,
            "texte": "Retour"
        }

    def _creer_boutons(self):
        boutons = {}
        noms_modes = ["Joueur VS Joueur", "Joueur VS IA", "En ligne"]
        largeur, hauteur = 400, 80
        espacement = 40
        total_h = len(noms_modes) * hauteur + (len(noms_modes) - 1) * espacement
        x = self.LARGEUR // 2 - largeur // 2
        y_start = self.HAUTEUR // 2 - total_h // 2

        for i, nom in enumerate(noms_modes):
            y = y_start + i * (hauteur + espacement)
            boutons[nom] = {
                "rect": pygame.Rect(x, y, largeur, hauteur),
                "couleur": self.NOIR,
                "texte": nom
            }
        return boutons

    def dessiner(self):
        self.ecran.blit(self.background_image, (0, 0))
        police_titre = pygame.font.Font(self.font_path, 48)
        police_bouton = pygame.font.Font(self.font_path, 32)
        police_retour = pygame.font.Font(self.font_path, 28)

        # Titre avec le nom du jeu sélectionné
        titre = police_titre.render(f"Mode de jeu - {self.jeu}", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, 200))
        self.ecran.blit(titre, rect_titre)

        for bouton in self.boutons.values():
            pygame.draw.rect(self.ecran, bouton["couleur"], bouton["rect"], border_radius=30)
            pygame.draw.rect(self.ecran, self.BLANC, bouton["rect"], 3, border_radius=30)
            texte = police_bouton.render(bouton["texte"], True, self.BLANC)
            rect_texte = texte.get_rect(center=bouton["rect"].center)
            self.ecran.blit(texte, rect_texte)

        pygame.draw.rect(self.ecran, self.bouton_retour["couleur"], self.bouton_retour["rect"], border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour["rect"], 2, border_radius=15)
        texte_retour = police_retour.render(self.bouton_retour["texte"], True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour["rect"].center)
        self.ecran.blit(texte_retour, rect_texte_retour)

    def executer(self):
        en_cours = True
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if self.bouton_retour["rect"].collidepoint(x, y):
                        en_cours = False
                    for nom, info in self.boutons.items():
                        if info["rect"].collidepoint(x, y):
                            self.lancer_jeu(nom)
                            en_cours = False

            self.dessiner()
            pygame.display.flip()

    def lancer_jeu(self, mode):
        print(f"Lancement du jeu {self.jeu} en mode {mode}")
        
        if self.jeu == "Congress":
            try:
                # Sélection du plateau pour Congress
                from Board.board_complet import SelecteurPlateau
                selecteur = SelecteurPlateau()
                plateau_final = selecteur.executer()
                if plateau_final:
                    from Jeux.Congress.congress_rules import Plateau_pion
                    
                    # Essayer différentes façons d'initialiser selon la signature de la classe
                    try:
                        # Essai 1: avec le mode comme paramètre
                        jeu = Plateau_pion(mode)
                    except TypeError:
                        try:
                            # Essai 2: sans paramètre, puis définir le mode
                            jeu = Plateau_pion()
                            if hasattr(jeu, 'mode'):
                                jeu.mode = mode
                            elif hasattr(jeu, 'set_mode'):
                                jeu.set_mode(mode)
                        except:
                            # Essai 3: juste créer l'instance basique
                            jeu = Plateau_pion()
                    
                    jeu.run()
                    
            except ImportError as e:
                print("Erreur lors de l'import du jeu Congress:", e)
            except Exception as e:
                print(f"Erreur lors du lancement de Congress: {e}")
                
        elif self.jeu == "Katarenga":
            try:
                # Lancer Katarenga avec le mode sélectionné
                print(f"Lancement de Katarenga en mode {mode}")
                # TODO: Intégrer le code pour lancer Katarenga
                # from Jeux.Katarenga.katarenga_main import Katarenga
                # jeu = Katarenga(mode)
                # jeu.run()
            except ImportError as e:
                print("Erreur lors de l'import du jeu Katarenga:", e)
                
        elif self.jeu == "Isolation":
            try:
                # Lancer Isolation avec le mode sélectionné
                print(f"Lancement d'Isolation en mode {mode}")
                # TODO: Intégrer le code pour lancer Isolation
                # from Jeux.Isolation.isolation_main import Isolation
                # jeu = Isolation(mode)
                # jeu.run()
            except ImportError as e:
                print("Erreur lors de l'import du jeu Isolation:", e)

if __name__ == "__main__":
    # Test avec Congress par défaut
    menu = MenuMode("Congress")
    menu.executer()