# ui/login.py

import customtkinter as ctk
from tkinter import messagebox
from ui.dashboard_admin import AdminDashboard

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Connexion Admin")
        self.geometry("400x300")
        self.resizable(True, True)
        self.state("zoomed")
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Connexion Admin", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur", textvariable=self.username_var).pack(pady=10)
        ctk.CTkEntry(self, placeholder_text="Mot de passe", textvariable=self.password_var, show="*").pack(pady=10)

        ctk.CTkButton(self, text="Se connecter", command=self._login).pack(pady=20)

    def _login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        # Ici tu peux ajouter la vérification réelle avec la base de données
        if username == "admin" and password == "admin":
            self.destroy()
            AdminDashboard(self.master)
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")
