import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Admin
from werkzeug.security import generate_password_hash, check_password_hash
import sys 

class AdminLogin(ctk.CTkToplevel):
    def __init__(self, master=None, on_success=None):
        super().__init__(master)
        self.title("Connexion Administration")
        self.geometry("400x400")
        self.resizable(True, True)
        self.state("zoomed")
        self.on_success = on_success

        self.db = SessionLocal()
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        if self._admin_exists():
            self._build_login_form()
        else:
            self._build_create_form()

    def _admin_exists(self):
        return self.db.query(Admin).first() is not None

    def _build_login_form(self):
        ctk.CTkLabel(self, text="Connexion Admin", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 20))

        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        ctk.CTkLabel(self, text="Identifiant").pack(pady=(10, 5))
        self.username_entry = ctk.CTkEntry(self, textvariable=self.username_var, width=250)
        self.username_entry.pack()

        ctk.CTkLabel(self, text="Mot de passe").pack(pady=(20, 5))
        self.password_entry = ctk.CTkEntry(self, textvariable=self.password_var, show="*", width=250)
        self.password_entry.pack()

        ctk.CTkButton(self, text="Se connecter", command=self._login, width=200).pack(pady=(30, 10))
        
        ctk.CTkButton(self, text="Annuler", command=sys.exit, fg_color="gray", hover_color="darkgray", width=200).pack()

    def _build_create_form(self):
        ctk.CTkLabel(self, text="Créer un compte Admin", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 20))

        self.new_username_var = ctk.StringVar()
        self.new_password_var = ctk.StringVar()

        ctk.CTkLabel(self, text="Nom d'utilisateur").pack(pady=(10, 5))
        self.new_username_entry = ctk.CTkEntry(self, textvariable=self.new_username_var, width=250)
        self.new_username_entry.pack()

        ctk.CTkLabel(self, text="Mot de passe").pack(pady=(20, 5))
        self.new_password_entry = ctk.CTkEntry(self, textvariable=self.new_password_var, show="*", width=250)
        self.new_password_entry.pack()

        ctk.CTkButton(self, text="Créer le compte", command=self._create_admin, width=200).pack(pady=(30, 10))
        ctk.CTkButton(self, text="Annuler", command=sys.exit, fg_color="gray", hover_color="darkgray", width=200).pack()

    def _create_admin(self):
        username = self.new_username_var.get().strip()
        password = self.new_password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        if self.db.query(Admin).filter_by(username=username).first():
            messagebox.showerror("Erreur", "Ce nom d'utilisateur existe déjà.")
            return

        # hashed_pw = generate_password_hash(password)
        new_admin = Admin(username=username, password=password) 
        self.db.add(new_admin)
        self.db.commit()
        messagebox.showinfo("Succès", "Compte admin créé avec succès.")
        self.destroy()
        if self.on_success:
            self.on_success()

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        admin = self.db.query(Admin).filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            messagebox.showinfo("Succès", "Connexion réussie.")
            self.destroy()
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects.")

    def _valider_connexion(self):
        # ... validation
        # si OK:
        self.destroy()
        if self.on_success:
            self.on_success()        

    def destroy(self):
        self.db.close()
        super().destroy()
