import pygame
import sys
import socket
import pickle
import threading
import time

class ClientJeu:
    def __init__(self):
        self.client_socket = None
        self.connexion_active = False
        
        # État du jeu
        self.adversaire_plateaux = [None, None, None, None]
        self.joueur_pret = False
        self.adversaire_pret = False
        self.mode_jeu = "EDITION"  # Pour synchroniser avec l'hôte
    
    def connecter(self, ip, port, code_salon):
        """Se connecte au serveur de jeu"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.connexion_active = True
            
            # Démarrer le thread d'écoute
            thread_reception = threading.Thread(target=self.recevoir_donnees)
            thread_reception.daemon = True
            thread_reception.start()
            
            print(f"Connecté à l'hôte {ip}:{port} !")
            return True
            
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
    
    def recevoir_donnees(self):
        """Thread qui écoute les données entrantes du serveur"""
        while self.connexion_active:
            try:
                # Recevoir la taille des données
                taille_donnees = self.client_socket.recv(4)
                if not taille_donnees:
                    print("Connexion perdue avec le serveur")
                    self.connexion_active = False
                    break
                
                taille = int.from_bytes(taille_donnees, byteorder='big')
                
                # Recevoir les données
                donnees = b''
                while len(donnees) < taille:
                    chunk = self.client_socket.recv(min(4096, taille - len(donnees)))
                    if not chunk:
                        break
                    donnees += chunk
                
                # Désérialiser les données
                if donnees:
                    message = pickle.loads(donnees)
                    self.traiter_message(message)
                
            except Exception as e:
                print(f"Erreur dans la réception des données: {e}")
                self.connexion_active = False
                break
    
    def traiter_message(self, message):
        """Traite le message reçu du serveur"""
        type_message = message.get("type")
        contenu = message.get("contenu")
        
        if type_message == "plateau":
            # Mettre à jour les plateaux de l'adversaire
            self.adversaire_plateaux = contenu
            print("Plateaux adversaires mis à jour")
        
        elif type_message == "pret":
            # L'adversaire est prêt
            self.adversaire_pret = contenu
            print(f"Adversaire {'prêt' if contenu else 'pas prêt'}")
            
        elif type_message == "mode":
            # Changement de mode de jeu
            self.mode_jeu = contenu
            print(f"Mode de jeu changé: {contenu}")
    
    def envoyer_donnees(self, type_message, contenu):
        """Envoie des données au serveur"""
        if not self.client_socket or not self.connexion_active:
            print("Impossible d'envoyer des données: pas de connexion")
            return False
        
        try:
            message = {
                "type": type_message,
                "contenu": contenu
            }
            
            donnees = pickle.dumps(message)
            taille = len(donnees)
            
            # Envoyer d'abord la taille des données
            self.client_socket.sendall(taille.to_bytes(4, byteorder='big'))
            
            # Envoyer les données
            self.client_socket.sendall(donnees)
            return True
            
        except Exception as e:
            print(f"Erreur dans l'envoi des données: {e}")
            self.connexion_active = False
            return False
    
    def mettre_a_jour_plateaux(self, plateaux):
        """Met à jour l'état local des plateaux et envoie au serveur"""
        return self.envoyer_donnees("plateau", plateaux)
    
    def signaler_pret(self, est_pret):
        """Signale que le joueur est prêt"""
        self.joueur_pret = est_pret
        return self.envoyer_donnees("pret", est_pret)
    
    def fermer(self):
        """Ferme la connexion"""
        self.connexion_active = False
        if self.client_socket:
            self.client_socket.close()

class EditeurPlateau:
    def __init__(self):
        pygame.init()
        
        # Dimensions de l'écran
        self.LARGEUR_ECRAN = 1075
        self.LARGEUR_JEU = 800
        self.HAUTEUR_ECRAN = 800
        
        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (40, 40, 40)
        self.ROUGE = (173, 7, 60)
        self.BLEU = (29, 185, 242)
        self.JAUNE = (235, 226, 56)
        self.VERT = (24, 181, 87)
        self.GRIS = (100, 100, 100)
        
        # Dimensions de la grille
        self.TAILLE_GRILLE = 2
        self.TAILLE_CASE = self.LARGEUR_JEU // self.TAILLE_GRILLE
        
        # Dimensions des petits plateaux
        self.TAILLE_PETIT_PLATEAU = 4
        self.TAILLE_PETITE_CASE = self.TAILLE_CASE // self.TAILLE_PETIT_PLATEAU
        
        # Constantes du panneau d'édition
        self.POS_X_PANNEAU = self.LARGEUR_JEU
        self.LARGEUR_PANNEAU = self.LARGEUR_ECRAN - self.LARGEUR_JEU
        self.TAILLE_APERCU = 150
        self.MARGE_PANNEAU = 20
        
        # Initialisation de l'écran
        self.ecran = pygame.display.set_mode((self.LARGEUR_ECRAN, self.HAUTEUR_ECRAN))
        pygame.display.set_caption("Éditeur de Plateaux - Invité")
        
        # Création des petits plateaux
        self.petits_plateaux = [
            # Plateau 1 - Configuration standard
            [[self.ROUGE, self.BLEU, self.JAUNE, self.VERT], 
             [self.BLEU, self.VERT, self.ROUGE, self.JAUNE],
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU], 
             [self.VERT, self.JAUNE, self.BLEU, self.ROUGE]],
            
            # Plateau 2 - Configuration en spirale
            [[self.ROUGE, self.ROUGE, self.ROUGE, self.BLEU],
             [self.VERT, self.JAUNE, self.BLEU, self.BLEU],
             [self.VERT, self.ROUGE, self.JAUNE, self.BLEU],
             [self.VERT, self.VERT, self.VERT, self.JAUNE]],
            
            # Plateau 3 - Configuration en damier
            [[self.ROUGE, self.BLEU, self.ROUGE, self.BLEU],
             [self.BLEU, self.ROUGE, self.BLEU, self.ROUGE],
             [self.ROUGE, self.BLEU, self.ROUGE, self.BLEU],
             [self.BLEU, self.ROUGE, self.BLEU, self.ROUGE]],
            
            # Plateau 4 - Configuration diagonale
            [[self.ROUGE, self.VERT, self.BLEU, self.JAUNE],
             [self.JAUNE, self.ROUGE, self.VERT, self.BLEU],
             [self.BLEU, self.JAUNE, self.ROUGE, self.VERT],
             [self.VERT, self.BLEU, self.JAUNE, self.ROUGE]]
        ]
        
        # Variables de glisser-déposer
        self.plateau_selectionne = None
        self.position_selection = None
        self.rotation_selection = 0
        self.plateaux_places = [None, None, None, None]
        
        # État du jeu
        self.joueur_pret = False
        self.mode_jeu = "CONNEXION"  # Modes: CONNEXION, EDITION, ATTENTE, JEU
        
        # Initialisation du client
        self.client = ClientJeu()
        
        # Variables pour la connexion
        self.ip_hote = ""
        self.port_hote = 5000
        self.code_salon = ""
        self.saisie_active = "ip"  # ip, port, code
        self.texte_saisie = ""

    def dessiner_grand_plateau(self):
        # Dessiner le plateau principal du joueur
        for ligne in range(self.TAILLE_GRILLE):
            for colonne in range(self.TAILLE_GRILLE):
                rect = pygame.Rect(colonne * self.TAILLE_CASE, ligne * self.TAILLE_CASE, 
                                 self.TAILLE_CASE, self.TAILLE_CASE)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
        
        # Si en mode JEU, dessiner le plateau de l'adversaire
        if self.mode_jeu == "JEU" and self.client.connexion_active:
            # Dessiner le plateau adverse en petit
            for ligne in range(self.TAILLE_GRILLE):
                for colonne in range(self.TAILLE_GRILLE):
                    rect = pygame.Rect(
                        self.POS_X_PANNEAU + self.MARGE_PANNEAU + colonne * (self.TAILLE_APERCU // 2),
                        self.HAUTEUR_ECRAN // 2 + ligne * (self.TAILLE_APERCU // 2),
                        self.TAILLE_APERCU // 2, self.TAILLE_APERCU // 2
                    )
                    pygame.draw.rect(self.ecran, self.GRIS, rect)
                    pygame.draw.rect(self.ecran, self.BLANC, rect, 1)
            
            # Dessiner les petits plateaux de l'adversaire
            for idx, info_plateau in enumerate(self.client.adversaire_plateaux):
                if info_plateau is not None:
                    plateau, x, y, rotation = info_plateau
                    # Calculer position relative
                    grille_x = x // self.TAILLE_CASE
                    grille_y = y // self.TAILLE_CASE
                    
                    # Réduire la taille du plateau pour l'aperçu
                    taille_mini = (self.TAILLE_APERCU // 2) // self.TAILLE_PETIT_PLATEAU
                    
                    # Dessiner le plateau adverse en petit
                    for ligne in range(self.TAILLE_PETIT_PLATEAU):
                        for colonne in range(self.TAILLE_PETIT_PLATEAU):
                            if rotation == 0:
                                couleur = plateau[ligne][colonne]
                            elif rotation == 90:
                                couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - colonne][ligne]
                            elif rotation == 180:
                                couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - ligne][self.TAILLE_PETIT_PLATEAU - 1 - colonne]
                            elif rotation == 270:
                                couleur = plateau[colonne][self.TAILLE_PETIT_PLATEAU - 1 - ligne]
                            
                            rect_mini = pygame.Rect(
                                self.POS_X_PANNEAU + self.MARGE_PANNEAU + grille_x * (self.TAILLE_APERCU // 2) + colonne * taille_mini,
                                self.HAUTEUR_ECRAN // 2 + grille_y * (self.TAILLE_APERCU // 2) + ligne * taille_mini,
                                taille_mini, taille_mini
                            )
                            pygame.draw.rect(self.ecran, couleur, rect_mini)
                            pygame.draw.rect(self.ecran, self.BLANC, rect_mini, 1)

    def dessiner_petit_plateau(self, plateau, x, y, rotation):
        for ligne in range(self.TAILLE_PETIT_PLATEAU):
            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                if rotation == 0:
                    couleur = plateau[ligne][colonne]
                elif rotation == 90:
                    couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - colonne][ligne]
                elif rotation == 180:
                    couleur = plateau[self.TAILLE_PETIT_PLATEAU - 1 - ligne][self.TAILLE_PETIT_PLATEAU - 1 - colonne]
                elif rotation == 270:
                    couleur = plateau[colonne][self.TAILLE_PETIT_PLATEAU - 1 - ligne]

                rect = pygame.Rect(x + colonne * self.TAILLE_PETITE_CASE, 
                                 y + ligne * self.TAILLE_PETITE_CASE,
                                 self.TAILLE_PETITE_CASE, self.TAILLE_PETITE_CASE)
                pygame.draw.rect(self.ecran, couleur, rect)
                pygame.draw.rect(self.ecran, self.BLANC, rect, 1)

    def dessiner_panneau_edition(self):
        # Fond du panneau
        rect_panneau = pygame.Rect(self.POS_X_PANNEAU, 0, self.LARGEUR_PANNEAU, self.HAUTEUR_ECRAN)
        pygame.draw.rect(self.ecran, (60, 60, 60), rect_panneau)
        
        # Titre
        police = pygame.font.Font(None, 36)
        titre = police.render("Éditeur de Plateaux", True, self.BLANC)
        self.ecran.blit(titre, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, self.MARGE_PANNEAU))
        
        # Mode CONNEXION - Écran de connexion
        if self.mode_jeu == "CONNEXION":
            return self._dessiner_ecran_connexion()
        
        # Mode EDITION - Permettre la sélection et placement de plateaux
        elif self.mode_jeu == "EDITION":
            # Informations de connexion
            info_texte = "Connecté à l'hôte"
            info = police.render(info_texte, True, self.VERT)
            self.ecran.blit(info, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, self.HAUTEUR_ECRAN - 70))
            
            # Aperçu des plateaux disponibles
            for idx, plateau in enumerate(self.petits_plateaux):
                if all(self.plateaux_places[i] is None or self.plateaux_places[i][0] != plateau 
                      for i in range(4)):
                    self._dessiner_apercu_plateau(idx, plateau)

            # Vérifier si tous les plateaux sont placés
            tous_plateaux_places = all(plateau is not None for plateau in self.plateaux_places)
                    
            # Dessiner le bouton d'acceptation uniquement si tous les plateaux sont placés
            if tous_plateaux_places:
                # Position et dimensions du bouton
                bouton_x = self.POS_X_PANNEAU + self.MARGE_PANNEAU
                bouton_y = self.HAUTEUR_ECRAN - self.MARGE_PANNEAU - 110
                bouton_largeur = self.LARGEUR_PANNEAU - (2 * self.MARGE_PANNEAU)
                bouton_hauteur = 40
                            
                # Dessiner le bouton
                rect_bouton = pygame.Rect(bouton_x, bouton_y, bouton_largeur, bouton_hauteur)
                            
                # Changer la couleur si la souris survole le bouton
                souris_x, souris_y = pygame.mouse.get_pos()
                if rect_bouton.collidepoint(souris_x, souris_y):
                    couleur_bouton = (100, 200, 100)  # Vert plus clair sur survol
                else:
                    couleur_bouton = (50, 150, 50)  # Vert normal
                                
                pygame.draw.rect(self.ecran, couleur_bouton, rect_bouton)
                pygame.draw.rect(self.ecran, self.BLANC, rect_bouton, 2)
                            
                # Texte du bouton
                police = pygame.font.Font(None, 30)
                texte = police.render("Confirmer Plateau", True, self.BLANC)
                texte_rect = texte.get_rect(center=rect_bouton.center)
                self.ecran.blit(texte, texte_rect)
                
                return rect_bouton  # Renvoie le rectangle pour la détection de clic
                
        # Si en mode ATTENTE ou JEU, afficher les informations de status
        elif self.mode_jeu in ["ATTENTE", "JEU"]:
            # Statut
            statut_titre = police.render("Statut:", True, self.BLANC)
            self.ecran.blit(statut_titre, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, 80))
            
            # Information de votre statut
            vous_texte = f"Vous: {'Prêt' if self.joueur_pret else 'En attente'}"
            vous_couleur = self.VERT if self.joueur_pret else self.JAUNE
            vous_statut = police.render(vous_texte, True, vous_couleur)
            self.ecran.blit(vous_statut, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, 120))
            
            # Information du statut de l'adversaire
            adv_texte = f"Adversaire: {'Prêt' if self.client.adversaire_pret else 'En attente'}"
            adv_couleur = self.VERT if self.client.adversaire_pret else self.JAUNE
            adv_statut = police.render(adv_texte, True, adv_couleur)
            self.ecran.blit(adv_statut, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, 160))
            
            # Afficher une étiquette pour le plateau de l'adversaire
            if self.mode_jeu == "JEU":
                adv_label = police.render("Plateau adversaire:", True, self.BLANC)
                self.ecran.blit(adv_label, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, self.HAUTEUR_ECRAN // 2 - 40))
        
        return None
    
    def _dessiner_ecran_connexion(self):
        """Dessine l'écran de connexion"""
        # Police pour le texte
        police = pygame.font.Font(None, 30)
        police_saisie = pygame.font.Font(None, 36)
        
        # Dessiner les champs de saisie
        y_pos = 100
        
        # Champ IP
        texte_ip = police.render("Adresse IP de l'hôte:", True, self.BLANC)
        self.ecran.blit(texte_ip, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos))
        
        # Rectangle de saisie IP
        rect_ip = pygame.Rect(self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos + 30, 
                             self.LARGEUR_PANNEAU - (2 * self.MARGE_PANNEAU), 40)
        couleur_rect = (80, 80, 80) if self.saisie_active != "ip" else (100, 100, 100)
        pygame.draw.rect(self.ecran, couleur_rect, rect_ip)
        pygame.draw.rect(self.ecran, self.BLANC, rect_ip, 2)
        
        # Texte de l'IP
        texte_saisie_ip = police_saisie.render(self.ip_hote, True, self.BLANC)
        self.ecran.blit(texte_saisie_ip, (rect_ip.x + 10, rect_ip.y + 10))
        
        # Champ Port
        y_pos += 90
        texte_port = police.render("Port de l'hôte:", True, self.BLANC)
        self.ecran.blit(texte_port, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos))
        
        # Rectangle de saisie Port
        rect_port = pygame.Rect(self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos + 30, 
                               self.LARGEUR_PANNEAU - (2 * self.MARGE_PANNEAU), 40)
        couleur_rect = (80, 80, 80) if self.saisie_active != "port" else (100, 100, 100)
        pygame.draw.rect(self.ecran, couleur_rect, rect_port)
        pygame.draw.rect(self.ecran, self.BLANC, rect_port, 2)
        
        # Texte du Port
        port_str = str(self.port_hote) if self.port_hote else ""
        texte_saisie_port = police_saisie.render(port_str, True, self.BLANC)
        self.ecran.blit(texte_saisie_port, (rect_port.x + 10, rect_port.y + 10))
        
        # Champ Code salon
        y_pos += 90
        texte_code = police.render("Code salon:", True, self.BLANC)
        self.ecran.blit(texte_code, (self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos))
        
        # Rectangle de saisie Code
        rect_code = pygame.Rect(self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos + 30, 
                               self.LARGEUR_PANNEAU - (2 * self.MARGE_PANNEAU), 40)
        couleur_rect = (80, 80, 80) if self.saisie_active != "code" else (100, 100, 100)
        pygame.draw.rect(self.ecran, couleur_rect, rect_code)
        pygame.draw.rect(self.ecran, self.BLANC, rect_code, 2)
        
        # Texte du Code
        texte_saisie_code = police_saisie.render(self.code_salon, True, self.BLANC)
        self.ecran.blit(texte_saisie_code, (rect_code.x + 10, rect_code.y + 10))
        
        # Bouton de connexion
        y_pos += 90
        rect_bouton = pygame.Rect(self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos, 
                                 self.LARGEUR_PANNEAU - (2 * self.MARGE_PANNEAU), 50)
        
        # Changer la couleur si la souris survole le bouton
        souris_x, souris_y = pygame.mouse.get_pos()
        if rect_bouton.collidepoint(souris_x, souris_y):
            couleur_bouton = (100, 200, 100)
        else:
            couleur_bouton = (50, 150, 50)
        
        pygame.draw.rect(self.ecran, couleur_bouton, rect_bouton)
        pygame.draw.rect(self.ecran, self.BLANC, rect_bouton, 2)
        
        # Texte du bouton
        texte = police.render("Se connecter", True, self.BLANC)
        texte_rect = texte.get_rect(center=rect_bouton.center)
        self.ecran.blit(texte, texte_rect)
        
        # Retourner les zones cliquables
        return {
            "ip": rect_ip,
            "port": rect_port,
            "code": rect_code,
            "bouton": rect_bouton
        }
        
    def _dessiner_apercu_plateau(self, idx, plateau):
        y_pos = idx * (self.TAILLE_APERCU + self.MARGE_PANNEAU) + 80
        rect_apercu = pygame.Rect(self.POS_X_PANNEAU + self.MARGE_PANNEAU, y_pos, 
                                self.TAILLE_APERCU, self.TAILLE_APERCU)
        pygame.draw.rect(self.ecran, (80, 80, 80), rect_apercu)
        pygame.draw.rect(self.ecran, self.BLANC, rect_apercu, 2)
        
        taille_mini = self.TAILLE_APERCU // self.TAILLE_PETIT_PLATEAU
        for ligne in range(self.TAILLE_PETIT_PLATEAU):
            for colonne in range(self.TAILLE_PETIT_PLATEAU):
                couleur = plateau[ligne][colonne]
                rect_mini = pygame.Rect(
                    self.POS_X_PANNEAU + self.MARGE_PANNEAU + colonne * taille_mini,
                    y_pos + ligne * taille_mini,
                    taille_mini, taille_mini
                )
                pygame.draw.rect(self.ecran, couleur, rect_mini)
                pygame.draw.rect(self.ecran, self.BLANC, rect_mini, 1)

    def executer(self):
        en_cours = True
        horloge = pygame.time.Clock()

        while en_cours:
            self.ecran.fill(self.NOIR)
            self.dessiner_grand_plateau()
            resultat_panneau = self.dessiner_panneau_edition()
            self._gerer_plateaux_places()
            
            try:
                en_cours = self._gerer_evenements(resultat_panneau)
            except Exception as e:
                print(f"Erreur non gérée: {e}")
                pygame.event.clear()

            self._dessiner_plateau_selectionne()
            pygame.display.flip()
            horloge.tick(60)  # Limite à 60 FPS

        # Fermer proprement la connexion
        if self.client.connexion_active:
            self.client.fermer()
        pygame.quit()
        sys.exit()

    def _gerer_plateaux_places(self):
        for idx, info_plateau in enumerate(self.plateaux_places):
            if info_plateau is not None:
                plateau, x, y, rotation = info_plateau
                self.dessiner_petit_plateau(plateau, x, y, rotation)

    def _gerer_evenements(self, zones_cliquables):
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                return False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:  # Quitter avec Échap
                    return False
                
                # Gérer la saisie de texte pour la connexion
                if self.mode_jeu == "CONNEXION" and self.saisie_active:
                    self._gerer_saisie_texte(evenement)
            
            # Gestion des clics selon le mode
            if evenement.type == pygame.MOUSEBUTTONDOWN:
                # Mode connexion: gérer les zones de saisie
                if self.mode_jeu == "CONNEXION" and isinstance(zones_cliquables, dict):
                    for zone, rect in zones_cliquables.items():
                        if rect.collidepoint(evenement.pos):
                            if zone == "bouton":
                                # Tenter de se connecter
                                if self.ip_hote and self.port_hote:
                                    if self.client.connecter(self.ip_hote, self.port_hote, self.code_salon):
                                        self.mode_jeu = "EDITION"
                            else:
                                # Activer la zone de saisie
                                self.saisie_active = zone
                
                # Mode EDITION: vérifier si on a cliqué sur le bouton d'acceptation
                elif self.mode_jeu == "EDITION" and isinstance(zones_cliquables, pygame.Rect):
                    if zones_cliquables.collidepoint(evenement.pos):
                        # Passer en mode attente et envoyer les plateaux
                        self.mode_jeu = "ATTENTE"
                        self.joueur_pret = True
                        
                        # Envoyer les plateaux et le statut
                        if self.client.connexion_active:
                            self.client.mettre_a_jour_plateaux(self.plateaux_places)
                            self.client.signaler_pret(True)
            
            # Synchroniser le mode de jeu avec le client
            if self.client.connexion_active and self.client.mode_jeu != self.mode_jeu:
                # Si le client passe en JEU, suivre
                if self.client.mode_jeu == "JEU":
                    self.mode_jeu = "JEU"
            
            # Si en mode EDITION, gérer le glisser-déposer
            if self.mode_jeu == "EDITION":
                self._gerer_clic_souris(evenement)
                self._gerer_relache_souris(evenement)
                self._gerer_rotation(evenement)
                self._gerer_mouvement_souris(evenement)
        
        return True
    
    def _gerer_saisie_texte(self, evenement):
        """Gère la saisie de texte pour les champs de connexion"""
        if evenement.key == pygame.K_RETURN or evenement.key == pygame.K_TAB:
            # Passer au champ suivant
            if self.saisie_active == "ip":
                self.saisie_active = "port"
            elif self.saisie_active == "port":
                self.saisie_active = "code"
            elif self.saisie_active == "code":
                self.saisie_active = "ip"
        elif evenement.key == pygame.K_BACKSPACE:
            # Effacer le dernier caractère
            if self.saisie_active == "ip":
                self.ip_hote = self.ip_hote[:-1]
            elif self.saisie_active == "port":
                self.port_hote = int(str(self.port_hote)[:-1]) if len(str(self.port_hote)) > 1 else 0
            elif self.saisie_active == "code":
                self.code_salon = self.code_salon[:-1]
        else:
            # Ajouter le caractère si c'est un caractère valide
            if evenement.unicode.isprintable():
                if self.saisie_active == "ip":
                    self.ip_hote += evenement.unicode
                elif self.saisie_active == "port" and evenement.unicode.isdigit():
                    # Convertir en entier
                    self.port_hote = int(str(self.port_hote) + evenement.unicode) if self.port_hote else int(evenement.unicode)
                elif self.saisie_active == "code":
                    self.code_salon += evenement.unicode

    def _gerer_clic_souris(self, evenement):
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            souris_x, souris_y = evenement.pos
            
            # Vérifier si le clic est dans le panneau d'édition
            if self.POS_X_PANNEAU <= souris_x <= self.LARGEUR_ECRAN:
                idx = (souris_y - 80) // (self.TAILLE_APERCU + self.MARGE_PANNEAU)
                if 0 <= idx < len(self.petits_plateaux):
                    if all(self.plateaux_places[i] is None or 
                          self.plateaux_places[i][0] != self.petits_plateaux[idx] 
                          for i in range(4)):
                        self.plateau_selectionne = idx
                        self.position_selection = evenement.pos
            
            # Vérifier si un plateau placé est cliqué
            else:
                for idx, info_plateau in enumerate(self.plateaux_places):
                    if info_plateau is not None:
                        plateau, x, y, rotation = info_plateau
                        if (x <= souris_x < x + self.TAILLE_CASE and 
                            y <= souris_y < y + self.TAILLE_CASE):
                            self.plateau_selectionne = self.petits_plateaux.index(plateau)
                            self.position_selection = evenement.pos
                            self.rotation_selection = rotation
                            self.plateaux_places[idx] = None
                            break

    def _gerer_relache_souris(self, evenement):
        if (evenement.type == pygame.MOUSEBUTTONUP and 
            self.plateau_selectionne is not None):
            souris_x, souris_y = evenement.pos
            
            if souris_x < self.LARGEUR_JEU:  # Placement uniquement dans la zone de jeu
                grille_x = souris_x // self.TAILLE_CASE
                grille_y = souris_y // self.TAILLE_CASE
                
                if 0 <= grille_x < self.TAILLE_GRILLE and 0 <= grille_y < self.TAILLE_GRILLE:
                    index_cible = grille_y * self.TAILLE_GRILLE + grille_x
                    
                    plateau_existant = self.plateaux_places[index_cible]
                    self.plateaux_places[index_cible] = (
                        self.petits_plateaux[self.plateau_selectionne],
                        grille_x * self.TAILLE_CASE,
                        grille_y * self.TAILLE_CASE,
                        self.rotation_selection
                    )
                    
                    if plateau_existant is not None:
                        ancien_plateau, _, _, ancienne_rotation = plateau_existant
                        self.plateau_selectionne = self.petits_plateaux.index(ancien_plateau)
                        self.rotation_selection = ancienne_rotation
                        self.position_selection = evenement.pos
                    else:
                        self.plateau_selectionne = None
                        self.position_selection = None

    def _gerer_rotation(self, evenement):
        if (evenement.type == pygame.KEYDOWN and 
            self.plateau_selectionne is not None):
            if evenement.key == pygame.K_r:  # Rotation avec la touche R
                self.rotation_selection = (self.rotation_selection + 90) % 360

    def _gerer_mouvement_souris(self, evenement):
        if (evenement.type == pygame.MOUSEMOTION and 
            self.plateau_selectionne is not None and 
            self.position_selection is not None):
            self.position_selection = evenement.pos

    def _dessiner_plateau_selectionne(self):
        if self.plateau_selectionne is not None and self.position_selection is not None:
            souris_x, souris_y = self.position_selection
            self.dessiner_petit_plateau(
                self.petits_plateaux[self.plateau_selectionne],
                souris_x - self.TAILLE_PETITE_CASE * 2,
                souris_y - self.TAILLE_PETITE_CASE * 2,
                self.rotation_selection
            )

if __name__ == "__main__":
    editeur = EditeurPlateau()
    editeur.executer()