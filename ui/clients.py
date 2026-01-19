# ui/clients.py

import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Client

from ui.modifier_client import ModifierClient

class ClientManager(ctk.CTkToplevel):
    def __init__(self, master=None, on_close=None):
        super().__init__(master)
        self.title("Gestion des Clients")
        self.on_close = on_close
        self.protocol("WM_DELETE_WINDOW", self._fermer)
        self.geometry("800x600")
        self.resizable(True, True)
        self.state("zoomed")
        self.selected_client_id = ctk.StringVar()
        self.search_var = ctk.StringVar()
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="👤 Gestion des Clients", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # boutons de recherche

        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=10)

        ctk.CTkButton(top_frame, text="← Retour", command=self._retour_dashboard).grid(row=0, column=0, padx=10)

        ctk.CTkButton(top_frame, text="Ajouter", command=self._ajouter_client).grid(row=0, column=1, padx=10)

        ctk.CTkButton(top_frame, text="Modifier", command=self._modifier_client).grid(row=0, column=2, padx=10)
        
        ctk.CTkButton(top_frame, text="Supprimer", command=self._supprimer_client, fg_color="red", hover_color="darkred").grid(row=0, column=3, padx=10)


        # Barre de recherche
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=(0, 10))
        
        ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Rechercher par nom, prénom ou email", width=300).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(search_frame, text="Rechercher", command=self._rechercher_client).grid(row=0, column=1, padx=5)
        
        ctk.CTkButton(search_frame, text="Réinitialiser", command=self._reset_recherche, fg_color="gray", hover_color="darkgray").grid(row=0, column=2, padx=5)

        # Liste des clients
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(pady=10, fill="both", expand=True)

        
        
        self._load_clients()

    def _load_clients(self):
        db = SessionLocal()
        clients = db.query(Client).all()
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not clients:
            ctk.CTkLabel(self.table_frame, text="Aucun client enregistré.", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=20)
        else:
            for c in clients:
                label = f"{c.nom} {c.prenom} - {c.email}"
                ctk.CTkRadioButton(self.table_frame, text=label, variable=self.selected_client_id, value=str(c.id)).pack(anchor="w", padx=20, pady=5)
        db.close()

    def _rechercher_client(self):
        db = SessionLocal()
        query = self.search_var.get().strip().lower()
        clients = db.query(Client).filter(
            (Client.nom.ilike(f"%{query}%")) |
            (Client.prenom.ilike(f"%{query}%")) |
            (Client.email.ilike(f"%{query}%"))
        ).all()
        
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        if not clients:
            ctk.CTkLabel(self.table_frame, text="Aucun client trouvé.", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=20)
        else:
            for c in clients:
                label = f"{c.nom} {c.prenom} - {c.email}"
                ctk.CTkRadioButton(self.table_frame, text=label, variable=self.selected_client_id, value=str(c.id)).pack(anchor="w", padx=20, pady=5)
        db.close()
        
        ctk.CTkLabel(self, text=f"{len(clients)} client(s) affiché(s)", font=ctk.CTkFont(size=14)).pack(pady=(0, 10))

        messagebox.showinfo("Recherche terminée", f"{len(clients)} résultat(s) trouvé(s).")
    def _reset_recherche(self):
        self.search_var.set("")
        self._load_clients()

    def _ajouter_client(self):
        from ui.ajouter_client import AjouterClient
        AjouterClient(self, on_success=self._load_clients)


    def _modifier_client(self):
        client_id = self.selected_client_id.get()
        if not client_id:
          messagebox.showwarning("Aucun client sélectionné", "Veuillez sélectionner un client à modifier.")
          return

        
        ModifierClient(self, client_id=int(client_id), on_success=self._load_clients)


    def _supprimer_client(self):
        client_id = self.selected_client_id.get()
        if not client_id:
            messagebox.showwarning("Aucun client sélectionné", "Veuillez sélectionner un client à supprimer.")
            return

        confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce client ?")
        if not confirm:
            return

        db = SessionLocal()
        client = db.query(Client).filter_by(id=int(client_id)).first()
        if client:
            db.delete(client)
            db.commit()
            messagebox.showinfo("Succès", "Client supprimé avec succès.")
            self._load_clients()
        else:
            messagebox.showerror("Erreur", "Client introuvable.")
        db.close()

    def _retour_dashboard(self):
            self.destroy()
            from ui.dashboard_admin import AdminDashboard
            AdminDashboard(self.master)
    
    def _fermer(self):
        if self.on_close:
            self.on_close()
        self.destroy()