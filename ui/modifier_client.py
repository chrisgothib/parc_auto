# ui/modifier_client.py

import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Client

class ModifierClient(ctk.CTkToplevel):
    def __init__(self, master=None, client_id=None, on_success=None):
        super().__init__(master)
        self.title("Modifier un client")
        self.geometry("400x450")
        self.resizable(True, True)
        self.state("zoomed")
        self.client_id = client_id
        self.on_success = on_success
        self.db = SessionLocal()
        self._build_ui()

    def _build_ui(self):
        client = self.db.query(Client).filter_by(id=self.client_id).first()
        if not client:
            messagebox.showerror("Erreur", "Client introuvable.")
            self.destroy()
            return

        self.nom_var = ctk.StringVar(value=client.nom)
        self.prenom_var = ctk.StringVar(value=client.prenom)
        self.adresse_var = ctk.StringVar(value=client.adresse or "")
        self.email_var = ctk.StringVar(value=client.email)

        ctk.CTkLabel(self, text="Modifier un client", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        champs = [
            ("Nom", self.nom_var),
            ("Prénom", self.prenom_var),
            ("Adresse", self.adresse_var),
            ("Email", self.email_var)
        ]

        for label, var in champs:
            ctk.CTkLabel(self, text=label).pack(pady=(10, 0))
            ctk.CTkEntry(self, textvariable=var, width=250).pack()

        ctk.CTkButton(self, text="Enregistrer", command=self._modifier, width=200).pack(pady=(30, 10))
        ctk.CTkButton(self, text="Annuler", command=self.destroy, fg_color="gray", hover_color="darkgray", width=200).pack()

    def _modifier(self):
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        adresse = self.adresse_var.get().strip()
        email = self.email_var.get().strip()

        if not nom or not prenom or not email:
            messagebox.showerror("Erreur", "Nom, prénom et email sont obligatoires.")
            return

        client = self.db.query(Client).filter_by(id=self.client_id).first()
        if not client:
            messagebox.showerror("Erreur", "Client introuvable.")
            return

        # Vérifie si l'email est déjà utilisé par un autre client
        email_existe = self.db.query(Client).filter(Client.email == email, Client.id != self.client_id).first()
        if email_existe:
            messagebox.showerror("Erreur", "Cet email est déjà utilisé par un autre client.")
            return

        client.nom = nom
        client.prenom = prenom
        client.adresse = adresse
        client.email = email

        self.db.commit()
        messagebox.showinfo("Succès", "Client modifié avec succès.")
        self.destroy()
        if self.on_success:
            self.on_success()

    def destroy(self):
        self.db.close()
        super().destroy()
