# ui/vehicules.py

import customtkinter as ctk
from tkinter import messagebox

class VehiculeManager(ctk.CTkToplevel):
    def __init__(self, master=None, on_close=None):
        super().__init__(master)
        self.title("Gestion des Véhicules")
        self.geometry("900x600")
        self.resizable(True, True)
        self.state("zoomed")
        self.on_close = on_close
        self.protocol("WM_DELETE_WINDOW", self._fermer)
        self._build_ui()
        



    def _build_ui(self):
        ctk.CTkLabel(self, text="🚗 Gestion des Véhicules", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        self.search_var = ctk.StringVar()
        self.selected_vehicule_id = ctk.StringVar()
        self.type_filter_var = ctk.StringVar(value="Tous")

        # 🔼 Boutons d’action en haut
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=10)

        ctk.CTkButton(top_frame, text="← Retour", command=self._retour_dashboard).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(top_frame, text="Ajouter", command=self._ajouter_vehicule).grid(row=0, column=1, padx=10)
        
        ctk.CTkButton(top_frame, text="Modifier", command=self._modifier_vehicule).grid(row=0, column=2, padx=10)
        
        ctk.CTkButton(top_frame, text="Supprimer", command=self._supprimer_vehicule, fg_color="red", hover_color="darkred").grid(row=0, column=3, padx=10)
        
        ctk.CTkButton(top_frame, text="🔄 Rafraîchir", command=self._load_vehicules).grid(row=0, column=4, padx=10)

        # 🔍 Barre de recherche
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=(0, 10))

        ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Rechercher...", width=300).grid(row=0, column=0, padx=10)
    
        ctk.CTkOptionMenu(search_frame, values=["Tous", "Voiture", "Moto"], variable=self.type_filter_var).grid(row=0, column=1, padx=10)
        
        ctk.CTkButton(search_frame, text="Rechercher", command=self._rechercher_vehicule).grid(row=0, column=2, padx=10)

        # Tableau des véhicules (mocké pour l’instant)
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(pady=10, fill="both", expand=True)
        self._load_vehicules()

        
    def _load_vehicules(self):
        from core.database import SessionLocal
        from core.models import Vehicule, Voiture, Moto

        db = SessionLocal()
        vehicules = db.query(Vehicule).all()

        for widget in self.table_frame.winfo_children():
          widget.destroy()

        for v in vehicules:
          if v.type == "voiture":
              label = f"🚗 {v.marque} {v.modele} - {v.immatriculation} | {v.nb_portes} portes"
          elif v.type == "moto":
              label = f"🏍️ {v.marque} {v.modele} - {v.immatriculation} | {v.cylindree} cm³"
          else:
              label = f"{v.marque} {v.modele} - {v.immatriculation}"

          ctk.CTkRadioButton(
            self.table_frame,
            text=label,
            variable=self.selected_vehicule_id,
            value=str(v.id)
            ).pack(anchor="w", padx=20, pady=5)

        if not vehicules:
          ctk.CTkLabel(self.table_frame, text="Aucun véhicule enregistré.", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=20)
  

        db.close()


    def _ajouter_vehicule(self):
      from ui.ajouter_vehicule import AjouterVehicule
      AjouterVehicule(self, on_success=self._load_vehicules)


    def _modifier_vehicule(self):
        vehicule_id = self.selected_vehicule_id.get()
        if not vehicule_id:
            messagebox.showwarning("Aucun véhicule sélectionné", "Veuillez sélectionner un véhicule à modifier.")
            return

        from ui.modifier_vehicule import ModifierVehicule
        ModifierVehicule(self, vehicule_id=int(vehicule_id), on_success=self._load_vehicules)


    def _supprimer_vehicule(self):
        from core.models import Vehicule
        from core.database import SessionLocal

        vehicule_id = self.selected_vehicule_id.get()
        if not vehicule_id:
            messagebox.showwarning("Aucun véhicule sélectionné", "Veuillez sélectionner un véhicule à supprimer.")
            return

        confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce véhicule ?")
        if not confirm:
            return

        db = SessionLocal()
        vehicule = db.query(Vehicule).filter_by(id=int(vehicule_id)).first()

        if vehicule:
            db.delete(vehicule)
            db.commit()
            messagebox.showinfo("Succès", "Véhicule supprimé avec succès.")
            self._load_vehicules()
        else:
            messagebox.showerror("Erreur", "Véhicule introuvable.")


    def _rechercher_vehicule(self):
        from core.database import SessionLocal
        from core.models import Vehicule

        query = self.search_var.get().strip().lower()
        type_filter = self.type_filter_var.get().lower()
        db = SessionLocal()

        vehicules = db.query(Vehicule)

        if type_filter in ["voiture", "moto"]:
            vehicules = vehicules.filter(Vehicule.type == type_filter)

        if query:
            vehicules = vehicules.filter(
            (Vehicule.marque.ilike(f"%{query}%")) |
            (Vehicule.modele.ilike(f"%{query}%")) |
            (Vehicule.immatriculation.ilike(f"%{query}%"))
        )

        vehicules = vehicules.all()

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not vehicules:
            ctk.CTkLabel(self.table_frame, text="Aucun véhicule trouvé.", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=20)
        else:
            for v in vehicules:
                if v.type == "voiture":
                    label = f"🚗 {v.marque} {v.modele} - {v.immatriculation} | {v.nb_portes} portes"
                elif v.type == "moto":
                    label = f"🏍️ {v.marque} {v.modele} - {v.immatriculation} | {v.cylindree} cm³"
                else:
                    label = f"{v.marque} {v.modele} - {v.immatriculation}"

                ctk.CTkRadioButton(
                    self.table_frame,
                    text=label,
                    variable=self.selected_vehicule_id,
                    value=str(v.id)
                ).pack(anchor="w", padx=20, pady=5)
            messagebox.showinfo("Recherche terminée", f"{len(vehicules)} résultat(s) trouvé(s).")    

        db.close()
        
    def _retour_dashboard(self):
            self.destroy()
            from ui.dashboard_admin import AdminDashboard
            AdminDashboard(self.master)
    

    def _reset_recherche(self):
        self.search_var.set("")
        self.type_filter_var.set("Tous")
        self._load_vehicules()


    def _fermer(self):
        if self.on_close:
            self.on_close()
        self.destroy()    
    


