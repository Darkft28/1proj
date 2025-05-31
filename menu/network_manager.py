import pygame
import sys
import socket
import threading
import random
import string
import json
import os
from config import get_theme

class NetworkManager:
    def __init__(self, jeu_nom):
        pygame.init()
        self.jeu_nom = jeu_nom  # "Katarenga", "Isolation", ou "Congress"
        
        # Configuration de l'écran
        info = pygame.display.Info()
        self.LARGEUR = info.current_w
        self.HAUTEUR = info.current_h
        self.ecran = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption(f"Réseau - {self.jeu_nom}")
        
        # Police et thème
        self.font_path = 'assets/police-gloomie_saturday/Gloomie Saturday.otf'
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
        self.VERT = (24, 181, 87)
        self.GRIS = (128, 128, 128)
        self.JAUNE = (235, 226, 56)
        
        # État du réseau
        self.mode = None  # "host" ou "guest"
        self.socket_serveur = None
        self.socket_client = None
        self.connexion_etablie = False
        self.code_salon = None
        self.ip_locale = self.obtenir_ip_locale()
        self.port = 5555
        
        # Interface
        self.ecran_actuel = "menu"  # "menu", "host_attente", "guest_connexion", "jeu"
        self.message_erreur = ""
        self.message_copie = ""
        self.temps_copie = 0
        
        # Champs de saisie pour guest
        self.ip_input = ""
        self.code_input = ""
        self.champ_actif = "ip"
        
        # Variables de jeu
        self.jeu_instance = None
        self.mon_numero = None  # 1 pour host, 2 pour guest
        self.adversaire_deconnecte = False
        
        # Signaux pour communication entre threads
        self._signal_demarrer_jeu_host = False
        self._signal_demarrer_jeu_guest = False
        
        # Import de pyperclip si disponible
        try:
            import pyperclip
            self.pyperclip = pyperclip
        except ImportError:
            self.pyperclip = None
    
    def obtenir_ip_locale(self):
        """Obtient l'adresse IP locale de la machine"""
        try:
            # Créer une connexion temporaire pour obtenir l'IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def generer_code_salon(self):
        """Génère un code aléatoire à 6 chiffres"""
        return ''.join(random.choices(string.digits, k=6))
    
    def dessiner_menu_principal(self):
        """Dessine le menu principal avec les options Host/Rejoindre/Retour"""
        self.ecran.blit(self.background_image, (0, 0))
        
        try:
            police_titre = pygame.font.Font(self.font_path, 48)
            police_bouton = pygame.font.Font(self.font_path, 32)
            police_retour = pygame.font.Font(self.font_path, 28)
        except:
            police_titre = pygame.font.Font(None, 48)
            police_bouton = pygame.font.Font(None, 32)
            police_retour = pygame.font.Font(None, 28)
        
        # Titre
        titre = police_titre.render(f"Réseau - {self.jeu_nom}", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, 200))
        self.ecran.blit(titre, rect_titre)
        
        # Boutons
        largeur_bouton = 400
        hauteur_bouton = 80
        espacement = 40
        x_centre = self.LARGEUR // 2 - largeur_bouton // 2
        y_centre = self.HAUTEUR // 2 - hauteur_bouton
        
        # Bouton Héberger
        self.bouton_host = pygame.Rect(x_centre, y_centre, largeur_bouton, hauteur_bouton)
        pygame.draw.rect(self.ecran, self.NOIR, self.bouton_host, border_radius=30)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_host, 3, border_radius=30)
        texte_host = police_bouton.render("Héberger une partie", True, self.BLANC)
        rect_texte_host = texte_host.get_rect(center=self.bouton_host.center)
        self.ecran.blit(texte_host, rect_texte_host)
        
        # Bouton Rejoindre
        y_rejoindre = y_centre + hauteur_bouton + espacement
        self.bouton_guest = pygame.Rect(x_centre, y_rejoindre, largeur_bouton, hauteur_bouton)
        pygame.draw.rect(self.ecran, self.NOIR, self.bouton_guest, border_radius=30)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_guest, 3, border_radius=30)
        texte_guest = police_bouton.render("Rejoindre une partie", True, self.BLANC)
        rect_texte_guest = texte_guest.get_rect(center=self.bouton_guest.center)
        self.ecran.blit(texte_guest, rect_texte_guest)
        
        # Bouton Retour
        self.bouton_retour = pygame.Rect(50, 50, 120, 40)
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_retour, border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour, 2, border_radius=15)
        texte_retour = police_retour.render("Retour", True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour.center)
        self.ecran.blit(texte_retour, rect_texte_retour)
    
    def dessiner_ecran_host_attente(self):
        """Dessine l'écran d'attente pour l'hôte"""
        self.ecran.blit(self.background_image, (0, 0))
        
        try:
            police_titre = pygame.font.Font(self.font_path, 48)
            police_info = pygame.font.Font(self.font_path, 28)
            police_code = pygame.font.Font(self.font_path, 36)
            police_bouton = pygame.font.Font(self.font_path, 24)
        except:
            police_titre = pygame.font.Font(None, 48)
            police_info = pygame.font.Font(None, 28)
            police_code = pygame.font.Font(None, 36)
            police_bouton = pygame.font.Font(None, 24)
        
        # Titre
        titre = police_titre.render("En attente d'un adversaire...", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, 200))
        self.ecran.blit(titre, rect_titre)
        
        # Informations de connexion
        y_info = 350
        
        # IP
        texte_ip = police_info.render(f"Votre IP: {self.ip_locale}", True, self.BLANC)
        rect_ip = texte_ip.get_rect(center=(self.LARGEUR//2, y_info))
        self.ecran.blit(texte_ip, rect_ip)
        
        # Code
        texte_code_label = police_info.render("Code de la partie:", True, self.BLANC)
        rect_code_label = texte_code_label.get_rect(center=(self.LARGEUR//2, y_info + 80))
        self.ecran.blit(texte_code_label, rect_code_label)
        
        texte_code = police_code.render(self.code_salon, True, self.JAUNE)
        rect_code = texte_code.get_rect(center=(self.LARGEUR//2, y_info + 130))
        self.ecran.blit(texte_code, rect_code)
        
        # Boutons de copie si pyperclip est disponible
        if self.pyperclip:
            # Bouton copier IP
            self.bouton_copier_ip = pygame.Rect(self.LARGEUR//2 + 150, y_info - 20, 100, 40)
            pygame.draw.rect(self.ecran, self.BLEU, self.bouton_copier_ip, border_radius=10)
            texte_copier_ip = police_bouton.render("Copier", True, self.BLANC)
            rect_texte_copier_ip = texte_copier_ip.get_rect(center=self.bouton_copier_ip.center)
            self.ecran.blit(texte_copier_ip, rect_texte_copier_ip)
            
            # Bouton copier code
            self.bouton_copier_code = pygame.Rect(self.LARGEUR//2 + 150, y_info + 110, 100, 40)
            pygame.draw.rect(self.ecran, self.BLEU, self.bouton_copier_code, border_radius=10)
            texte_copier_code = police_bouton.render("Copier", True, self.BLANC)
            rect_texte_copier_code = texte_copier_code.get_rect(center=self.bouton_copier_code.center)
            self.ecran.blit(texte_copier_code, rect_texte_copier_code)
        
        # Message de copie
        if self.message_copie and pygame.time.get_ticks() - self.temps_copie < 2000:
            texte_copie = police_bouton.render(self.message_copie, True, self.VERT)
            rect_copie = texte_copie.get_rect(center=(self.LARGEUR//2, y_info + 200))
            self.ecran.blit(texte_copie, rect_copie)
        
        # Bouton Retour
        self.bouton_retour = pygame.Rect(50, 50, 120, 40)
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_retour, border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour, 2, border_radius=15)
        texte_retour = police_bouton.render("Retour", True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour.center)
        self.ecran.blit(texte_retour, rect_texte_retour)
    
    def dessiner_ecran_guest_connexion(self):
        """Dessine l'écran de connexion pour l'invité"""
        self.ecran.blit(self.background_image, (0, 0))
        
        try:
            police_titre = pygame.font.Font(self.font_path, 48)
            police_info = pygame.font.Font(self.font_path, 28)
            police_input = pygame.font.Font(self.font_path, 24)
            police_bouton = pygame.font.Font(self.font_path, 24)
        except:
            police_titre = pygame.font.Font(None, 48)
            police_info = pygame.font.Font(None, 28)
            police_input = pygame.font.Font(None, 24)
            police_bouton = pygame.font.Font(None, 24)
        
        # Titre
        titre = police_titre.render("Rejoindre une partie", True, self.BLANC)
        rect_titre = titre.get_rect(center=(self.LARGEUR//2, 200))
        self.ecran.blit(titre, rect_titre)
        
        # Champs de saisie
        y_base = self.HAUTEUR // 2 - 100
        
        # Champ IP
        label_ip = police_info.render("Adresse IP de l'hôte:", True, self.BLANC)
        self.ecran.blit(label_ip, (self.LARGEUR // 2 - 300, y_base - 40))
        
        rect_ip = pygame.Rect(self.LARGEUR // 2 - 300, y_base, 600, 50)
        couleur_ip = self.BLEU if self.champ_actif == "ip" else self.GRIS
        pygame.draw.rect(self.ecran, self.BLANC, rect_ip)
        pygame.draw.rect(self.ecran, couleur_ip, rect_ip, 3)
        
        texte_ip = police_input.render(self.ip_input, True, self.NOIR)
        self.ecran.blit(texte_ip, (rect_ip.x + 10, rect_ip.y + 10))
        
        # Champ Code
        y_code = y_base + 100
        label_code = police_info.render("Code de la partie:", True, self.BLANC)
        self.ecran.blit(label_code, (self.LARGEUR // 2 - 300, y_code - 40))
        
        rect_code = pygame.Rect(self.LARGEUR // 2 - 300, y_code, 600, 50)
        couleur_code = self.BLEU if self.champ_actif == "code" else self.GRIS
        pygame.draw.rect(self.ecran, self.BLANC, rect_code)
        pygame.draw.rect(self.ecran, couleur_code, rect_code, 3)
        
        texte_code = police_input.render(self.code_input, True, self.NOIR)
        self.ecran.blit(texte_code, (rect_code.x + 10, rect_code.y + 10))
        
        # Bouton Connexion
        largeur_bouton = 250
        hauteur_bouton = 60
        self.bouton_connexion = pygame.Rect(
            self.LARGEUR // 2 - largeur_bouton // 2,
            y_code + 100,
            largeur_bouton,
            hauteur_bouton
        )
        
        # Activer le bouton seulement si les deux champs sont remplis
        if self.ip_input and self.code_input:
            pygame.draw.rect(self.ecran, self.VERT, self.bouton_connexion, border_radius=20)
            texte_connexion = police_bouton.render("Se connecter", True, self.BLANC)
        else:
            pygame.draw.rect(self.ecran, self.GRIS, self.bouton_connexion, border_radius=20)
            texte_connexion = police_bouton.render("Se connecter", True, self.BLANC)
        
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_connexion, 3, border_radius=20)
        rect_texte_connexion = texte_connexion.get_rect(center=self.bouton_connexion.center)
        self.ecran.blit(texte_connexion, rect_texte_connexion)
        
        # Message d'erreur
        if self.message_erreur:
            texte_erreur = police_bouton.render(self.message_erreur, True, self.ROUGE)
            rect_erreur = texte_erreur.get_rect(center=(self.LARGEUR//2, y_code + 200))
            self.ecran.blit(texte_erreur, rect_erreur)
        
        # Instructions
        instructions = [
            "Tapez TAB pour passer d'un champ à l'autre",
            "Ctrl+V pour coller depuis le presse-papiers",
            "Entrée pour se connecter"
        ]
        
        y_instructions = self.HAUTEUR - 200
        for i, instruction in enumerate(instructions):
            texte_inst = police_bouton.render(instruction, True, self.BLANC)
            rect_inst = texte_inst.get_rect(center=(self.LARGEUR//2, y_instructions + i * 30))
            self.ecran.blit(texte_inst, rect_inst)
        
        # Bouton Retour
        self.bouton_retour = pygame.Rect(50, 50, 120, 40)
        pygame.draw.rect(self.ecran, self.ROUGE, self.bouton_retour, border_radius=15)
        pygame.draw.rect(self.ecran, self.BLANC, self.bouton_retour, 2, border_radius=15)
        texte_retour = police_bouton.render("Retour", True, self.BLANC)
        rect_texte_retour = texte_retour.get_rect(center=self.bouton_retour.center)
        self.ecran.blit(texte_retour, rect_texte_retour)
    
    def demarrer_serveur(self):
        """Démarre le serveur en mode host"""
        try:
            self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_serveur.bind((self.ip_locale, self.port))
            self.socket_serveur.listen(1)
            print(f"Serveur démarré sur {self.ip_locale}:{self.port}")
            
            self.mode = "host"
            self.ecran_actuel = "host_attente"
            self.code_salon = self.generer_code_salon()
            
            # Démarrer l'attente de connexion dans un thread séparé
            thread_serveur = threading.Thread(target=self._attendre_connexion)
            thread_serveur.daemon = True
            thread_serveur.start()
            
        except Exception as e:
            print(f"Erreur serveur: {e}")
            self.message_erreur = f"Erreur serveur: {e}"
    
    def _attendre_connexion(self):
        """Attendre une connexion dans un thread séparé"""
        try:
            # Attendre une connexion
            self.socket_client, adresse_client = self.socket_serveur.accept()
            print(f"Client connecté depuis {adresse_client}")
            
            # Attendre le code de validation
            message = self.socket_client.recv(1024).decode()
            if message.startswith("CODE:"):
                code_recu = message.split(":")[1]
                if code_recu == self.code_salon:
                    self.socket_client.send("OK".encode())
                    self.connexion_etablie = True
                    print("Connexion validée!")
                    
                    # Signaler au thread principal de démarrer le jeu
                    self._signal_demarrer_jeu_host = True
                else:
                    self.socket_client.send("ERREUR".encode())
                    self.socket_client.close()
                    self.socket_client = None
                    
        except Exception as e:
            print(f"Erreur connexion serveur: {e}")
            self.connexion_etablie = False
    
    def se_connecter_au_serveur(self, ip, code):
        """Se connecte au serveur en mode guest"""
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.settimeout(10)  # Timeout de 10 secondes
            self.socket_client.connect((ip, self.port))
            
            # Envoyer le code pour validation
            self.socket_client.send(f"CODE:{code}".encode())
            
            # Attendre la réponse
            reponse = self.socket_client.recv(1024).decode()
            if reponse == "OK":
                self.connexion_etablie = True
                self.mode = "guest"
                print("Connexion réussie!")
                
                # Signaler au thread principal de démarrer le jeu
                self._signal_demarrer_jeu_guest = True
                return True
            else:
                self.socket_client.close()
                self.socket_client = None
                self.message_erreur = "Code incorrect"
                return False
                
        except Exception as e:
            print(f"Erreur connexion: {e}")
            self.message_erreur = f"Erreur de connexion: {e}"
            if self.socket_client:
                self.socket_client.close()
                self.socket_client = None
            return False
    
    def lancer_jeu_host(self):
        """Lance le jeu en mode host (joueur 1)"""
        self.mon_numero = 1
        self.ecran_actuel = "jeu"
        
        if self.jeu_nom == "Katarenga":
            from Jeux.Katarenga.katarenga_rules import Plateau_pion
            self.jeu_instance = Plateau_pion(
                mode_reseau="host",
                socket_reseau=self.socket_client,
                mon_numero=1,
                connexion_etablie=True  # Important: s'assurer que c'est True
            )
            # Ajouter l'instance network_manager au jeu
            self.jeu_instance.network_manager = self
        elif self.jeu_nom == "Isolation":
            from Jeux.Isolation.isolation_rules import Plateau_pion
            self.jeu_instance = Plateau_pion(
                mode_reseau="host",
                socket_reseau=self.socket_client,
                mon_numero=1,
                connexion_etablie=True
            )
            self.jeu_instance.network_manager = self
    
        # Lancer le jeu
        if self.jeu_instance:
            # Envoyer signal de début
            self.socket_client.send("START".encode())
            self.jeu_instance.run()
    
    def lancer_jeu_guest(self):
        """Lance le jeu en mode guest (joueur 2)"""
        self.mon_numero = 2
        self.ecran_actuel = "jeu"
        
        if self.jeu_nom == "Katarenga":
            from Jeux.Katarenga.katarenga_rules import Plateau_pion
            self.jeu_instance = Plateau_pion(
                mode_reseau="guest",
                socket_reseau=self.socket_client,
                mon_numero=2,
                connexion_etablie=True
            )
            self.jeu_instance.network_manager = self
            self.jeu_instance.joueur_actuel = 1  # Commencer avec le joueur 1 (host)
        elif self.jeu_nom == "Isolation":
            from Jeux.Isolation.isolation_rules import Plateau_pion
            self.jeu_instance = Plateau_pion(
                mode_reseau="guest",
                socket_reseau=self.socket_client,
                mon_numero=2,
                connexion_etablie=True
            )
            self.jeu_instance.network_manager = self
            self.jeu_instance.joueur_actuel = 1  # Host commence
    
        # Lancer le jeu
        if self.jeu_instance:
            # Attendre signal de début
            message = self.socket_client.recv(1024).decode()
            if message == "START":
                self.jeu_instance.run()
    
    def selectionner_plateau(self):
        """Sélectionne un plateau pour le jeu"""
        try:
            # Lire le plateau final
            with open("plateau_final/plateau_finale.json", "r") as f:
                plateau_data = json.load(f)
            return plateau_data
        except Exception as e:
            print(f"Erreur lors du chargement du plateau: {e}")
            return None
    
    def gerer_evenements_menu(self, event):
        """Gère les événements dans le menu principal"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bouton_host.collidepoint(event.pos):
                self.demarrer_serveur()
            elif self.bouton_guest.collidepoint(event.pos):
                self.ecran_actuel = "guest_connexion"
            elif self.bouton_retour.collidepoint(event.pos):
                return "retour"
        
        return "continuer"
    
    def gerer_evenements_host_attente(self, event):
        """Gère les événements sur l'écran d'attente host"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bouton_retour.collidepoint(event.pos):
                # Nettoyer les connexions
                if self.socket_serveur:
                    self.socket_serveur.close()
                    self.socket_serveur = None
                if self.socket_client:
                    self.socket_client.close()
                    self.socket_client = None
                self.connexion_etablie = False
                self.ecran_actuel = "menu"
            elif self.pyperclip and hasattr(self, 'bouton_copier_ip') and self.bouton_copier_ip.collidepoint(event.pos):
                self.pyperclip.copy(self.ip_locale)
                self.message_copie = "IP copiée!"
                self.temps_copie = pygame.time.get_ticks()
            elif self.pyperclip and hasattr(self, 'bouton_copier_code') and self.bouton_copier_code.collidepoint(event.pos):
                self.pyperclip.copy(self.code_salon)
                self.message_copie = "Code copié!"
                self.temps_copie = pygame.time.get_ticks()
        
        return "continuer"
    
    def gerer_evenements_guest_connexion(self, event):
        """Gère les événements sur l'écran de connexion guest"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bouton_retour.collidepoint(event.pos):
                self.ecran_actuel = "menu"
                self.message_erreur = ""
            elif self.bouton_connexion.collidepoint(event.pos) and self.ip_input and self.code_input:
                if self.se_connecter_au_serveur(self.ip_input, self.code_input):
                    pass  # Le jeu démarre automatiquement via le signal
            
            # Gestion des clics dans les champs
            rect_ip = pygame.Rect(self.LARGEUR // 2 - 300, self.HAUTEUR // 2 - 100, 600, 50)
            rect_code = pygame.Rect(self.LARGEUR // 2 - 300, self.HAUTEUR // 2, 600, 50)
            
            if rect_ip.collidepoint(event.pos):
                self.champ_actif = "ip"
            elif rect_code.collidepoint(event.pos):
                self.champ_actif = "code"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.champ_actif = "code" if self.champ_actif == "ip" else "ip"
                
            elif event.key == pygame.K_BACKSPACE:
                if self.champ_actif == "ip":
                    self.ip_input = self.ip_input[:-1]
                else:
                    self.code_input = self.code_input[:-1]
                    
            elif event.key == pygame.K_RETURN and self.ip_input and self.code_input:
                if self.se_connecter_au_serveur(self.ip_input, self.code_input):
                    pass  # Le jeu démarre automatiquement via le signal
                    
            elif event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
                # Coller depuis le presse-papiers
                if self.pyperclip:
                    try:
                        texte_colle = self.pyperclip.paste()
                        if self.champ_actif == "ip":
                            self.ip_input = texte_colle
                        else:
                            self.code_input = texte_colle
                    except:
                        pass
                        
            elif event.unicode.isprintable():
                # Ajouter le caractère tapé
                if self.champ_actif == "ip":
                    self.ip_input += event.unicode
                else:
                    if event.unicode.isdigit() and len(self.code_input) < 6:
                        self.code_input += event.unicode
        
        return "continuer"
    
    def envoyer_mouvement(self, socket, depart, arrivee):
        """Envoie un mouvement au serveur/client"""
        try:
            message = f"MOVE:{depart[0]},{depart[1]}:{arrivee[0]},{arrivee[1]}"
            socket.send(message.encode())
            return True
        except Exception as e:
            print(f"Erreur envoi mouvement: {e}")
            return False

    def recevoir_mouvement(self, socket):
        """Reçoit un mouvement du serveur/client"""
        try:
            message = socket.recv(1024).decode()
            if message.startswith("MOVE:"):
                _, dep, arr = message.split(":")
                dl, dc = map(int, dep.split(","))
                al, ac = map(int, arr.split(","))
                return (dl, dc), (al, ac)
            return None
        except Exception as e:
            print(f"Erreur réception mouvement: {e}")
            return None
    
    def executer(self):
        """Boucle principale du gestionnaire réseau"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif self.ecran_actuel == "menu":
                    resultat = self.gerer_evenements_menu(event)
                    if resultat == "retour":
                        running = False
                        
                elif self.ecran_actuel == "host_attente":
                    self.gerer_evenements_host_attente(event)
                    
                elif self.ecran_actuel == "guest_connexion":
                    self.gerer_evenements_guest_connexion(event)
            
            # Vérifier les signaux pour démarrer les jeux
            if self._signal_demarrer_jeu_host:
                self._signal_demarrer_jeu_host = False
                self.lancer_jeu_host()
                running = False  # Sortir de la boucle après avoir lancé le jeu
                
            elif self._signal_demarrer_jeu_guest:
                self._signal_demarrer_jeu_guest = False
                self.lancer_jeu_guest()
                running = False  # Sortir de la boucle après avoir lancé le jeu
            
            # Dessiner l'écran approprié
            if self.ecran_actuel == "menu":
                self.dessiner_menu_principal()
            elif self.ecran_actuel == "host_attente":
                self.dessiner_ecran_host_attente()
            elif self.ecran_actuel == "guest_connexion":
                self.dessiner_ecran_guest_connexion()
            
            pygame.display.flip()
            clock.tick(60)
        
        # Nettoyage
        if self.socket_client:
            self.socket_client.close()
        if self.socket_serveur:
            self.socket_serveur.close()
        

if __name__ == "__main__":
    if len(sys.argv) > 1:
        jeu = sys.argv[1]
    else:
        jeu = "Katarenga"  # Par défaut
    
    manager = NetworkManager(jeu)
    manager.executer()

# Dans __init__ de chaque classe Plateau_pion des jeux
def __init__(self, mode_reseau=None, socket_reseau=None, mon_numero=None, connexion_etablie=False):
    # ...existing code...
    if mode_reseau:
        self.thread_reception = threading.Thread(target=self.recevoir_mouvements)
        self.thread_reception.daemon = True
        self.thread_reception.start()

def recevoir_mouvements(self):
    """Thread de réception des mouvements"""
    while self.running:
        try:
            if self.socket_reseau:
                mouvement = self.network_manager.recevoir_mouvement(self.socket_reseau)
                if mouvement is None:  # Déconnexion
                    self.adversaire_deconnecte = True
                    break
                # ...traitement du mouvement...
        except:
            self.adversaire_deconnecte = True
            break

# Dans la méthode gerer_clic des jeux
def gerer_clic(self):
    if self.mode_reseau and self.joueur_actuel != self.mon_numero:
        return  # Pas son tour
    # ...reste du code...