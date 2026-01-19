# ui/ajouter_client.py

import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Client

class AjouterClient(ctk.CTkToplevel):
    def __init__(self, master=None, on_success=None):
        super().__init__(master)
        self.title("Ajouter un client")
        self.geometry("400x450")
        self.resizable(True, True)
        self.state("zoomed")
        self.on_success = on_success
        self.db = SessionLocal()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)


    def _build_ui(self):
        ctk.CTkLabel(self, text="Ajouter un client", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.nom_var = ctk.StringVar()
        self.prenom_var = ctk.StringVar()
        self.adresse_var = ctk.StringVar()
        self.email_var = ctk.StringVar()

        champs = [
            ("Nom", self.nom_var),
            ("Prénom", self.prenom_var),
            ("Adresse", self.adresse_var),
            ("Email", self.email_var)
        ]

        for label, var in champs:
            ctk.CTkLabel(self, text=label).pack(pady=(10, 0))
            ctk.CTkEntry(self, textvariable=var, width=250).pack()

        ctk.CTkButton(self, text="Ajouter", command=self._ajouter, width=200).pack(pady=(30, 10))
        ctk.CTkButton(self, text="Annuler", command=self.destroy, fg_color="gray", hover_color="darkgray", width=200).pack()

    def _ajouter(self):
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        adresse = self.adresse_var.get().strip()
        email = self.email_var.get().strip()

        if not nom or not prenom or not email:
            messagebox.showerror("Erreur", "Nom, prénom et email sont obligatoires.")
            return

        if self.db.query(Client).filter_by(email=email).first():
            messagebox.showerror("Erreur", "Cet email est déjà utilisé.")
            return

        client = Client(nom=nom, prenom=prenom, adresse=adresse, email=email)
        self.db.add(client)
        self.db.commit()

        messagebox.showinfo("Succès", "Client ajouté avec succès.")
        self.destroy()
        if self.on_success:
            self.on_success()

    def destroy(self):
        self.db.close()
        super().destroy()
