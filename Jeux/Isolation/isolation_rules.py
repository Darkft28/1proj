import pygame
import sys
import json
from menu.config import get_theme

class Plateau_pion:
    def __init__(self):
        pygame.init()
        
        self.font_path = pygame.font.match_font('assets/police-gloomie_saturday/Gloomie Saturday.otf')
        
        # Obtenir la résolution de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h

        # Calcul des ratios d'échelle basé sur 2560x1440
        self.RATIO_X = self.LARGEUR / 2560
        self.RATIO_Y = self.HAUTEUR / 1440

        # Initialisation de la fenêtre de jeu
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Isolation - Jeu de Blocage")
        
        # Taille des cases
        self.TAILLE_CASE = int(120 * self.RATIO_X)
        self.OFFSET_X = (self.LARGEUR - 8 * self.TAILLE_CASE) // 2
        self.OFFSET_Y = (self.HAUTEUR - 8 * self.TAILLE_CASE) // 2
        
        # Fond d'écran
        theme = get_theme()
        if theme == "Sombre":
            self.background_image = pygame.image.load("assets/menu/menu-sombre.png")
        else:
            self.background_image = pygame.image.load("assets/menu/menu-claire.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.LARGEUR, self.HAUTEUR))

        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        self.GRIS = (128, 128, 128)
        self.ROUGE_CLAIR = (255, 100, 100)

        self.images = {}
        try:
            image_paths = {
                self.ROUGE: "assets/image_rouge.png",
                self.BLEU: "assets/image_bleue.png",
                self.JAUNE: "assets/image_jaune.png",
                self.VERT: "assets/image_verte.png"
            }
            for couleur, path in image_paths.items():
                self.images[couleur] = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Erreur lors du chargement des images: {e}")

        # Pions
        try:
            self.pion_blanc = pygame.image.load("assets/pion_blanc.png")
            self.pion_noir = pygame.image.load("assets/pion_noir.png")
        except:
            self.pion_blanc = None
            self.pion_noir = None

        # Plateau de base - 0 = vide, 1 = pion noir, 2 = pion blanc, -1 = case bloquée
        self.plateau = [[0 for _ in range(8)] for _ in range(8)]
        
        # Plateau des cases bloquées (pour visualisation)
        self.cases_bloquees = [[False for _ in range(8)] for _ in range(8)]
        
        # Configuration des boutons
        self.LARGEUR_BOUTON = int(400 * self.RATIO_X)
        self.HAUTEUR_BOUTON = int(80 * self.RATIO_Y)
        self.ESPACE_BOUTONS = int(40 * self.RATIO_Y)
        
        # État du jeu
        self.game_over = False
        self.gagnant = None

    def analyser_couleur_image(self, image_path):
        try:
            image = pygame.image.load(image_path)
            # Convertir en RGB pour analyse
            pixel_array = pygame.surfarray.array3d(image)
            
            # Calculer la couleur moyenne
            moyenne_r = pixel_array[:,:,0].mean()
            moyenne_g = pixel_array[:,:,1].mean()
            moyenne_b = pixel_array[:,:,2].mean()
            
            # Déterminer la couleur dominante
            if moyenne_r > 150 and moyenne_g < 100 and moyenne_b < 100:
                return self.ROUGE
            elif moyenne_r < 100 and moyenne_g < 100 and moyenne_b > 150:
                return self.BLEU
            elif moyenne_r < 100 and moyenne_g > 150 and moyenne_b < 100:
                return self.VERT
            elif moyenne_r > 200 and moyenne_g > 200 and moyenne_b < 150:
                return self.JAUNE
            else:
                # Couleur non identifiée, utiliser rouge par défaut
                return self.ROUGE
                
        except Exception as e:
            print(f"Erreur lors de l'analyse de couleur de {image_path}: {e}")
            return self.ROUGE

    def get_cases_bloquees_par_pion(self, ligne, col, couleur_case):
        cases_bloquees = []
        
        # Basé sur vos images des règles :
        if couleur_case == self.BLEU:  # Case bleue - mouvement de roi (8 directions adjacentes)
            directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
            for dl, dc in directions:
                nl, nc = ligne + dl, col + dc
                if 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))
                    
        elif couleur_case == self.VERT:  # Case verte - mouvement de cavalier (en L)
            mouvements_cavalier = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
            for dl, dc in mouvements_cavalier:
                nl, nc = ligne + dl, col + dc
                if 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))
                    
        elif couleur_case == self.JAUNE:  # Case jaune - mouvement de fou (diagonales jusqu'à obstacle)
            directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
            for dl, dc in directions:
                nl, nc = ligne + dl, col + dc
                while 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))
                    # S'arrêter si case occupée ou première case jaune rencontrée
                    if self.plateau[nl][nc] != 0 or self.get_couleur_case(nl, nc) == self.JAUNE:
                        break
                    nl, nc = nl + dl, nc + dc
                    
        elif couleur_case == self.ROUGE:  # Case rouge - mouvement de tour (lignes/colonnes jusqu'à obstacle)
            directions = [(-1,0), (1,0), (0,-1), (0,1)]
            for dl, dc in directions:
                nl, nc = ligne + dl, col + dc
                while 0 <= nl < 8 and 0 <= nc < 8:
                    cases_bloquees.append((nl, nc))
                    # S'arrêter si case occupée ou première case rouge rencontrée
                    if self.plateau[nl][nc] != 0 or self.get_couleur_case(nl, nc) == self.ROUGE:
                        break
                    nl, nc = nl + dl, nc + dc
                    
        return cases_bloquees

    def get_couleur_case(self, ligne, col):
        try:
            with open("plateaux/plateau_finale.json", 'r') as f:  # <-- ici
                plateau_images = json.load(f)
            
            # Adapter le plateau à 8x8 si nécessaire
            if len(plateau_images) < 8 or len(plateau_images[0]) < 8:
                plateau_complet = []
                for i in range(8):
                    ligne_data = []
                    for j in range(8):
                        ligne_data.append(plateau_images[i % len(plateau_images)][j % len(plateau_images[0])])
                    plateau_complet.append(ligne_data)
                plateau_images = plateau_complet
            
            # Récupérer le chemin de l'image pour cette case
            image_path = plateau_images[ligne][col]
            
            # Déterminer la couleur selon le nom/chemin de l'image
            if "rouge" in image_path.lower() or "red" in image_path.lower():
                return self.ROUGE
            elif "bleu" in image_path.lower() or "blue" in image_path.lower():
                return self.BLEU
            elif "vert" in image_path.lower() or "green" in image_path.lower():
                return self.VERT
            elif "jaune" in image_path.lower() or "yellow" in image_path.lower():
                return self.JAUNE
            else:
                # Fallback: analyser l'image pour détecter la couleur dominante
                return self.analyser_couleur_image(image_path)
                
        except Exception as e:
            print(f"Erreur lors de la détection de couleur: {e}")
            # Fallback vers le pattern original
            if (ligne + col) % 4 == 0:
                return self.ROUGE
            elif (ligne + col) % 4 == 1:
                return self.BLEU
            elif (ligne + col) % 4 == 2:
                return self.VERT
            else:
                return self.JAUNE

    def peut_placer_pion(self, ligne, col):
        # Case doit être vide et non bloquée
        return (0 <= ligne < 8 and 0 <= col < 8 and 
                self.plateau[ligne][col] == 0 and 
                not self.cases_bloquees[ligne][col])

    def placer_pion(self, ligne, col, joueur):
        if not self.peut_placer_pion(ligne, col):
            return False
            
        # Placer le pion
        self.plateau[ligne][col] = joueur
        
        # Obtenir la couleur de la case et bloquer les cases correspondantes
        couleur_case = self.get_couleur_case(ligne, col)
        cases_a_bloquer = self.get_cases_bloquees_par_pion(ligne, col, couleur_case)
        
        # Marquer les cases comme bloquées
        for bl, bc in cases_a_bloquer:
            if self.plateau[bl][bc] == 0:
                self.cases_bloquees[bl][bc] = True
                
        return True

    def verifier_fin_de_jeu(self):
        for i in range(8):
            for j in range(8):
                if self.peut_placer_pion(i, j):
                    return False
        return True

    def compter_cases_libres_par_joueur(self):
        # Dans cette version simplifiée, on compte juste les cases totalement libres
        cases_libres = 0
        for i in range(8):
            for j in range(8):
                if self.peut_placer_pion(i, j):
                    cases_libres += 1
        return cases_libres

    def run(self):
        # Redimensionner les pions si ils existent
        if self.pion_blanc and self.pion_noir:
            pion_size = int(self.TAILLE_CASE * 0.8)
            self.pion_blanc = pygame.transform.scale(self.pion_blanc, (pion_size, pion_size))
            self.pion_noir = pygame.transform.scale(self.pion_noir, (pion_size, pion_size))
        
        self.joueur_actuel = 1
        self.running = True
        
        while self.running:
            if self.background_image:
                self.ecran.blit(self.background_image, (0, 0))
            else:
                self.ecran.fill(self.BLANC)
            
            self.dessiner_plateau()
            self.afficher_pions()
            self.afficher_cases_bloquees()
            
            if not self.game_over:
                self.afficher_tour()
                self.afficher_info_jeu()
            else:
                self.afficher_fin_de_jeu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    x, y = event.pos
                    if self.bouton_abandonner and self.bouton_abandonner.collidepoint(x, y):
                        self.game_over = True
                        self.gagnant = "abandon"
                    else:
                        self.gerer_clic()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                    x, y = event.pos
                    if self.bouton_rejouer.collidepoint(x, y):
                        self.reinitialiser_jeu()
                    elif self.bouton_quitter.collidepoint(x, y):
                        self.running = False
            pygame.display.flip()
        
        pygame.quit()

    def reinitialiser_jeu(self):
        self.plateau = [[0 for _ in range(8)] for _ in range(8)]
        self.cases_bloquees = [[False for _ in range(8)] for _ in range(8)]
        self.joueur_actuel = 1
        self.game_over = False
        self.gagnant = None

    def dessiner_plateau(self):
        try:
            with open("plateaux/plateau_finale.json", 'r') as f:  # <-- ici aussi
                plateau_images = json.load(f)
            
            # Adapter le plateau à 8x8 si nécessaire
            if len(plateau_images) < 8 or len(plateau_images[0]) < 8:
                plateau_complet = []
                for i in range(8):
                    ligne = []
                    for j in range(8):
                        ligne.append(plateau_images[i % len(plateau_images)][j % len(plateau_images[0])])
                    plateau_complet.append(ligne)
                plateau_images = plateau_complet
            
            # Dessiner les images du plateau
            for i in range(8):
                for j in range(8):
                    image_path = plateau_images[i][j]
                    
                    if image_path not in self.images:
                        try:
                            self.images[image_path] = pygame.image.load(image_path).convert_alpha()
                            self.images[image_path] = pygame.transform.scale(self.images[image_path], 
                                                                           (self.TAILLE_CASE, self.TAILLE_CASE))
                        except:
                            # Fallback: utiliser la couleur calculée
                            couleur = self.get_couleur_case(i, j)
                            surface = pygame.Surface((self.TAILLE_CASE, self.TAILLE_CASE))
                            surface.fill(couleur)
                            self.images[image_path] = surface
                    
                    self.ecran.blit(self.images[image_path], 
                                  (self.OFFSET_X + j * self.TAILLE_CASE, 
                                   self.OFFSET_Y + i * self.TAILLE_CASE))
        except Exception as e:
            print(f"Erreur lors du chargement du plateau: {e}")
            # Fallback: dessiner avec les couleurs calculées
            for i in range(8):
                for j in range(8):
                    couleur = self.get_couleur_case(i, j)
                    pygame.draw.rect(self.ecran, couleur, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                     self.OFFSET_Y + i * self.TAILLE_CASE, 
                                     self.TAILLE_CASE, self.TAILLE_CASE))
                    
                    # Bordure noire
                    pygame.draw.rect(self.ecran, self.NOIR, 
                                    (self.OFFSET_X + j * self.TAILLE_CASE, 
                                     self.OFFSET_Y + i * self.TAILLE_CASE, 
                                     self.TAILLE_CASE, self.TAILLE_CASE), 2)

    def afficher_cases_bloquees(self):
        for i in range(8):
            for j in range(8):
                if self.cases_bloquees[i][j]:
                    # Case entièrement noire
                    pygame.draw.rect(self.ecran, self.NOIR, 
                                   (self.OFFSET_X + j * self.TAILLE_CASE, 
                                    self.OFFSET_Y + i * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))

    def afficher_pions(self):
        pion_size = int(self.TAILLE_CASE * 0.8)  
        offset = (self.TAILLE_CASE - pion_size) // 2
        for i in range(8):
            for j in range(8):
                if self.plateau[i][j] == 1:
                    if self.pion_noir:
                        self.ecran.blit(self.pion_noir,
                                        (self.OFFSET_X + j * self.TAILLE_CASE + offset,
                                         self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                    else:
                        # Fallback: cercle noir plus petit
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2)
                elif self.plateau[i][j] == 2:
                    if self.pion_blanc:
                        self.ecran.blit(self.pion_blanc,
                                        (self.OFFSET_X + j * self.TAILLE_CASE + offset,
                                         self.OFFSET_Y + i * self.TAILLE_CASE + offset))
                    else:
                        # Fallback: cercle blanc plus petit avec bordure noire
                        pygame.draw.circle(self.ecran, self.BLANC,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2)
                        pygame.draw.circle(self.ecran, self.NOIR,
                                         (self.OFFSET_X + j * self.TAILLE_CASE + self.TAILLE_CASE//2,
                                          self.OFFSET_Y + i * self.TAILLE_CASE + self.TAILLE_CASE//2),
                                         pion_size//2, 3)

    def afficher_tour(self):
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 35)
        joueur_nom = "Joueur 1" if self.joueur_actuel == 1 else "Joueur 2"
        texte = f"Tour de {joueur_nom} - Placez votre pion"
        couleur = self.NOIR if self.joueur_actuel == 1 else self.BLANC
        surface_texte = police.render(texte, True, couleur)
        self.ecran.blit(surface_texte, (self.LARGEUR // 2 - surface_texte.get_width() // 2, 70))

    def afficher_info_jeu(self):
        police = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 25)
        cases_libres = self.compter_cases_libres_par_joueur()
        texte = f"Cases libres restantes: {cases_libres}"
        surface_texte = police.render(texte, True, self.NOIR)
        self.ecran.blit(surface_texte, (20, self.HAUTEUR - 60))

        # Bouton abandonner (affiché seulement si la partie n'est pas finie)
        if not self.game_over:
            largeur_bouton = 220
            hauteur_bouton = 50
            self.bouton_abandonner = pygame.Rect(
                self.LARGEUR - largeur_bouton - 30,
                self.HAUTEUR - hauteur_bouton - 30,
                largeur_bouton,
                hauteur_bouton
            )
            pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_abandonner, border_radius=20)
            texte_abandonner = police.render("Abandonner", True, self.BLANC)
            rect_texte_abandonner = texte_abandonner.get_rect(center=self.bouton_abandonner.center)
            self.ecran.blit(texte_abandonner, rect_texte_abandonner)
        else:
            self.bouton_abandonner = None

    def afficher_fin_de_jeu(self):
        police_grand = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 40)
        gagnant_nom = "Joueur 2" if self.joueur_actuel == 1 else "Joueur 1"
        texte_principal = f"{gagnant_nom} gagne !"
        surface_principale = police_grand.render(texte_principal, True, self.BLANC)
        self.ecran.blit(surface_principale, (
            self.LARGEUR // 2 - surface_principale.get_width() // 2,
            self.HAUTEUR // 2 - 500
        ))

        # Bouton Rejouer
        largeur_bouton = 250
        hauteur_bouton = 60
        police_bouton = pygame.font.Font('assets/police-gloomie_saturday/Gloomie Saturday.otf', 32)
        self.bouton_rejouer = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton - 20,
            self.HAUTEUR // 2 - -450,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.BLEU, self.bouton_rejouer, border_radius=20)
        texte_rejouer = police_bouton.render("Rejouer", True, self.BLANC)
        rect_texte_rejouer = texte_rejouer.get_rect(center=self.bouton_rejouer.center)
        self.ecran.blit(texte_rejouer, rect_texte_rejouer)

        # Bouton Quitter
        self.bouton_quitter = pygame.Rect(
            self.LARGEUR // 2 + 20,
            self.HAUTEUR // 2 - -450,
            largeur_bouton,
            hauteur_bouton
        )
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_quitter, border_radius=20)
        texte_quitter = police_bouton.render("Quitter", True, self.BLANC)
        rect_texte_quitter = texte_quitter.get_rect(center=self.bouton_quitter.center)
        self.ecran.blit(texte_quitter, rect_texte_quitter)

    def gerer_clic(self):
        pos = pygame.mouse.get_pos()
        
        # Convertir la position en coordonnées de la grille
        col = (pos[0] - self.OFFSET_X) // self.TAILLE_CASE
        ligne = (pos[1] - self.OFFSET_Y) // self.TAILLE_CASE
        
        # Vérifier si le clic est dans les limites du plateau
        if 0 <= ligne < 8 and 0 <= col < 8:
            print(f"Clic sur la case ({ligne}, {col})")
            
            # Tenter de placer un pion
            if self.placer_pion(ligne, col, self.joueur_actuel):
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1                
                # Vérifier si le jeu est terminé
                if self.verifier_fin_de_jeu():
                    self.game_over = True
                    print("Jeu terminé!")                    
            else:
                print("Impossible de placer un pion ici!")

# Lancement du jeu
if __name__ == "__main__":
    jeu = Plateau_pion()
    jeu.run()