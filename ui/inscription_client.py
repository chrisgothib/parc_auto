# ui/inscription_client.py

import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Client


class InscriptionClient(ctk.CTkToplevel):
    def __init__(self, master=None, on_success=None):
        super().__init__(master)
        self.title("Créer un compte client")
        self.geometry("600x700")
        self.resizable(True, True)
        self.state("zoomed")
        self.on_success = on_success
        self._build_ui()
        self.after(200, lambda: self.email_entry.focus())
        self.after(100, lambda: self.focus_force())



    def _build_ui(self):
        ctk.CTkLabel(self, text="📝 Inscription Client", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.nom_var = ctk.StringVar()
        self.prenom_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.motdepasse_var = ctk.StringVar()
        self.confirm_var = ctk.StringVar()
        self.adresse_var = ctk.StringVar()

        champs = [
            ("Nom", self.nom_var),
            ("Prénom", self.prenom_var),
            ("Email", self.email_var),
            ("Mot de passe", self.motdepasse_var),
            ("Confirmer le mot de passe", self.confirm_var),
            ("Adresse", self.adresse_var)
        ]

        for label, var in champs:
            ctk.CTkLabel(self, text=label).pack(pady=(10, 0))
            show = "*" if "mot de passe" in label.lower() else None
            
            entry = ctk.CTkEntry(self, textvariable=var, show=show)
            entry.pack(pady=5)
            if "email" in label.lower():
                self.email_entry = entry  # ✅ pour pouvoir faire focus plus tard


        ctk.CTkButton(self, text="Créer le compte", command=self._creer_compte).pack(pady=30)

        

    def _creer_compte(self):
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        email = self.email_var.get().strip().lower()
        mdp = self.motdepasse_var.get()
        confirm = self.confirm_var.get()
        adresse = self.adresse_var.get().strip()

        if not all([nom, prenom, email, mdp, confirm]):
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs obligatoires.")
            return
        
        if len(mdp) < 6:
            messagebox.showwarning("Mot de passe trop court", "Le mot de passe doit contenir au moins 6 caractères.")
            return


        if mdp != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return
        
        

        db = SessionLocal()
        if db.query(Client).filter_by(email=email).first():
            messagebox.showerror("Erreur", "Un compte avec cet email existe déjà.")
            db.close()
            return

        from core.security import hasher_motdepasse

        motdepasse_hash = hasher_motdepasse(mdp)

        nouveau_client = Client(
        nom=nom,
        prenom=prenom,
        email=email,
        mot_de_passe=motdepasse_hash,
        adresse=adresse
        )


        db.add(nouveau_client)
        db.commit()
        db.close()

        messagebox.showinfo("Succès", "Compte créé avec succès. Vous pouvez maintenant vous connecter.")
        
        if self.on_success:
            self.on_success()
        self.destroy()

    
    