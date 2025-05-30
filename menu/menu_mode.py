import pygame
import sys
import os
import json
from .config import get_theme

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
        
        theme = get_theme()
        if theme == "Sombre":
            self.background_image = pygame.image.load("assets/menu/menu-sombre.png")
        else:
            self.background_image = pygame.image.load("assets/menu/menu-claire.png")
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

    def generer_plateau_katarenga(self):
        """
        Génère un plateau Katarenga 10x10 à partir du plateau_finale.json (8x8)
        Coins en (0,0), (0,9), (9,0), (9,9)
        Plateau final 8x8 placé entre (1,1) et (8,8)
        Reste = bordures
        Sauvegarde dans plateau_final/plateau_finale.json (écrase le plateau 8x8)
        """
        
        try:
            # Charger le plateau final 8x8
            with open("plateau_final/plateau_finale.json", 'r') as f:
                plateau_8x8 = json.load(f)
            
            # Créer le plateau 10x10 vide rempli de bordures
            plateau_10x10 = [["assets/bordure.png" for _ in range(10)] for _ in range(10)]
            
            # Placer les coins aux bonnes positions
            plateau_10x10[0][0] = "assets/coin.png"  # Coin haut-gauche
            plateau_10x10[0][9] = "assets/coin.png"  # Coin haut-droite  
            plateau_10x10[9][0] = "assets/coin.png"  # Coin bas-gauche
            plateau_10x10[9][9] = "assets/coin.png"  # Coin bas-droite
            
            # Placer le contenu 8x8 du plateau final entre (1,1) et (8,8)
            for i in range(8):
                for j in range(8):
                    plateau_10x10[i + 1][j + 1] = plateau_8x8[i][j]
            
            # Sauvegarder le nouveau plateau dans plateau_final (réécriture)
            with open("plateau_final/plateau_finale.json", 'w') as f:
                json.dump(plateau_10x10, f, indent=2)
            
            print("✅ Plateau Katarenga 10x10 généré avec succès !")
            print(f"   • Coins placés en (0,0), (0,9), (9,0), (9,9)")
            print(f"   • Plateau final 8x8 placé entre (1,1) et (8,8)")
            print(f"   • Bordures sur le reste du plateau")
            print(f"   • Sauvegardé dans plateau_final/plateau_finale.json")
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du plateau Katarenga: {e}")

    def lancer_jeu(self, mode):
        if mode == "En ligne":
            # Utiliser le gestionnaire réseau unifié pour tous les jeux
            try:
                from .network_manager import NetworkManager
                manager = NetworkManager(self.jeu)
                manager.executer()
            except ImportError as e:
                print("Erreur lors de l'import du gestionnaire réseau:", e)
            except Exception as e:
                print(f"Erreur lors du lancement du mode réseau: {e}")
        else:
            # Mode local (Joueur VS Joueur ou Joueur VS IA)
            if self.jeu == "Congress":
                try:
                    from Board.board_complet import SelecteurPlateau
                    selecteur = SelecteurPlateau()
                    plateau_final = selecteur.executer()
                    if plateau_final:
                        if mode == "Joueur VS IA":
                            from Jeux.Congress.congress_rules_IA import Plateau_pion
                            jeu = Plateau_pion()
                        else:
                            from Jeux.Congress.congress_rules import Plateau_pion
                            jeu = Plateau_pion()
                        jeu.run()
                except ImportError as e:
                    print("Erreur lors de l'import du jeu Congress:", e)
                except Exception as e:
                    print(f"Erreur lors du lancement de Congress: {e}")
                    
            elif self.jeu == "Katarenga":
                try:
                    from Board.board_complet import SelecteurPlateau
                    selecteur = SelecteurPlateau()
                    plateau_final = selecteur.executer()
                    if plateau_final:
                        # Ajouter les bordures au plateau_finale.json existant
                        self.generer_plateau_katarenga()
                        
                        if mode == "Joueur VS IA":
                            from Jeux.Katarenga.katarenga_rules_IA import Plateau_pion
                            jeu = Plateau_pion()
                            jeu.run()
                        else:
                            from Jeux.Katarenga.katarenga_rules import Plateau_pion
                            jeu = Plateau_pion()
                            jeu.run()
                except ImportError as e:
                    print("Erreur lors de l'import du jeu Katarenga:", e)
                except Exception as e:
                    print(f"Erreur lors du lancement de Katarenga: {e}")
                    
            elif self.jeu == "Isolation":
                try:
                    from Board.board_complet import SelecteurPlateau
                    selecteur = SelecteurPlateau()
                    plateau_final = selecteur.executer()
                    if plateau_final:
                        if mode == "Joueur VS IA":
                            from Jeux.Isolation.isolation_rules_IA import Plateau_pion
                            jeu = Plateau_pion()
                        else:
                            from Jeux.Isolation.isolation_rules import Plateau_pion
                            jeu = Plateau_pion()
                        jeu.run()
                except ImportError as e:
                    print("Erreur lors de l'import du jeu Isolation:", e)
                except Exception as e:
                    print(f"Erreur lors du lancement d'Isolation: {e}")

if __name__ == "__main__":
    # Test avec Congress par défaut
    menu = MenuMode("Congress")
    menu.executer()
