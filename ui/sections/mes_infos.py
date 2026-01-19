# ui/sections/mes_infos.py

import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Client

class MesInfosFrame(ctk.CTkFrame):
    def __init__(self, master=None, client=None):
        super().__init__(master)
        self.client = client
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="👤 Mes informations", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self.nom_var = ctk.StringVar(value=self.client.nom)
        self.prenom_var = ctk.StringVar(value=self.client.prenom)
        self.email_var = ctk.StringVar(value=self.client.email)
        self.adresse_var = ctk.StringVar(value=self.client.adresse or "")

        champs = [
            ("Nom", self.nom_var),
            ("Prénom", self.prenom_var),
            ("Email", self.email_var),
            ("Adresse", self.adresse_var)
        ]

        for label, var in champs:
            ctk.CTkLabel(self, text=label).pack(pady=(10, 0))
            ctk.CTkEntry(self, textvariable=var).pack(pady=5)

        ctk.CTkButton(self, text="Mettre à jour", command=self._mettre_a_jour).pack(pady=20)

    def _mettre_a_jour(self):
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        email = self.email_var.get().strip().lower()
        adresse = self.adresse_var.get().strip()

        if not all([nom, prenom, email]):
            messagebox.showwarning("Champs requis", "Nom, prénom et email sont obligatoires.")
            return

        db = SessionLocal()
        client_db = db.query(Client).filter_by(id=self.client.id).first()

        if client_db:
            client_db.nom = nom
            client_db.prenom = prenom
            client_db.email = email
            client_db.adresse = adresse
            db.commit()
            db.refresh(client_db)
            db.close()

            # Mise à jour de l'objet client local
            self.client.nom = nom
            self.client.prenom = prenom
            self.client.email = email
            self.client.adresse = adresse

            messagebox.showinfo("Succès", "Vos informations ont été mises à jour.")
        else:
            db.close()
            messagebox.showerror("Erreur", "Client introuvable.")
