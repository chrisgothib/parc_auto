# ui/accueil.py
import customtkinter as ctk
from PIL import Image, ImageTk
import os

class Accueil(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        # Titre principal
        ctk.CTkLabel(self, text="SYSTÈME DE LOCATION DE VÉHICULES",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(20, 10))

        # Logo
        try:
            logo_path = os.path.join("assets", "logo.png")
            image = Image.open(logo_path).resize((160, 160))
            self.logo_img = ImageTk.PhotoImage(image)
            ctk.CTkLabel(self, image=self.logo_img, text="").pack(pady=(0, 20))
        except Exception as e:
            print("Erreur chargement logo :", e)
            ctk.CTkLabel(self, text="(Logo manquant)", font=ctk.CTkFont(size=14, slant="italic")).pack(pady=(0, 20))

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Administration", command=self.lancer_admin, width=200).grid(row=0, column=0, padx=20)
        ctk.CTkButton(btn_frame, text="Client", command=self.lancer_client, width=200).grid(row=0, column=1, padx=20)

        ctk.CTkButton(btn_frame, text="Créer un compte", command=self.lancer_inscription, width=200).grid(row=1, column=0, columnspan=2, pady=10)

        ctk.CTkButton(btn_frame, text="Se connecter", command=self.lancer_connexion, width=200).grid(row=2, column=0, columnspan=2, pady=10)


    def lancer_admin(self):
        from ui.login_admin import AdminLogin
        AdminLogin(self)

    
    def lancer_inscription(self):
        from ui.inscription_client import InscriptionClient
        InscriptionClient(self, on_success=self.lancer_connexion)

    def lancer_connexion(self):
        from ui.connexion_client import ConnexionClient
        ConnexionClient(self)


  
