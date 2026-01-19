import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Client
from core.session import Session  # Singleton pour stocker l'utilisateur connecté
from ui.client_dashboard import ClientDashboard  # À créer ensuite

class ConnexionClient(ctk.CTkToplevel):
    def __init__(self, master=None, on_success=None):
        super().__init__(master)
        self.title("Connexion Client")
        self.geometry("400x400")
        self.resizable(True, True)
        self.state("zoomed")
        self.on_success = on_success  # ✅ Ajout du callback
        self._build_ui()
        self.after(100, lambda: self.focus_force())
        self.after(200, lambda: self.email_entry.focus())

    def _build_ui(self):
        ctk.CTkLabel(self, text="🔐 Connexion Client", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=30)

        self.email_var = ctk.StringVar()
        self.motdepasse_var = ctk.StringVar()

        ctk.CTkLabel(self, text="Email").pack(pady=(10, 0))
        self.email_entry = ctk.CTkEntry(self, textvariable=self.email_var)
        self.email_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Mot de passe").pack(pady=(10, 0))
        ctk.CTkEntry(self, textvariable=self.motdepasse_var, show="*").pack(pady=5)

        ctk.CTkButton(self, text="Se connecter", command=self._se_connecter).pack(pady=30)

        ctk.CTkButton(self, text="Créer un compte", command=self._ouvrir_inscription).pack(pady=10)

        ctk.CTkButton(self, text="Annuler", command=self._fermer_app, fg_color="gray", hover_color="darkgray").pack(pady=10)



    def _se_connecter(self):
        email = self.email_var.get().strip().lower()
        mdp = self.motdepasse_var.get()

        if not email or not mdp:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
            return

        db = SessionLocal()
        from core.security import hasher_motdepasse

        motdepasse_hash = hasher_motdepasse(mdp)
        client = db.query(Client).filter_by(email=email, mot_de_passe=motdepasse_hash).first()

        if client:
            Session.current_user = client
            messagebox.showinfo("Bienvenue", f"Bonjour {client.prenom} 👋")
            self.destroy()
            if self.on_success:
                self.on_success(client)  # ✅ Appel du callback avec le client
            else:
                ClientDashboard(self.master, client=client)
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect.")


    def _ouvrir_inscription(self):
        from ui.inscription_client import InscriptionClient
        InscriptionClient(self, on_success=self._reafficher_connexion)
        
    def _ouvrir_inscription(self):
            from ui.inscription_client import InscriptionClient
            InscriptionClient(self, on_success=self._reafficher_connexion)

    def _reafficher_connexion(self):
            ConnexionClient(self.master, on_success=self.on_success)
            self.destroy()

    def _fermer_app(self):
         import sys
         sys.exit()