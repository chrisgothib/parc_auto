import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Location, Client, Vehicule
from sqlalchemy import String, or_
import csv
from tkinter.filedialog import asksaveasfilename
from sqlalchemy.orm import joinedload


class LocationManager(ctk.CTkToplevel):
    def __init__(self, master=None, on_close=None):
        super().__init__(master)
        self.title("Gestion des Locations")
        self.on_close = on_close
        self.protocol("WM_DELETE_WINDOW", self._fermer)
        self.geometry("1000x600")
        self.resizable(True, True)
        self.state("zoomed")
        self.selected_location_id = ctk.StringVar()
        self._build_ui()

    def _build_ui(self):
        # Titre principal
            ctk.CTkLabel(
                self,
            text="📄 Gestion des Locations",
            font=ctk.CTkFont(size=24, weight="bold")
            ).pack(pady=20)

    # Variables de filtrage et de recherche
            self.tri_var = ctk.StringVar(value="toutes")  # Pour le tri général
            self.search_var = ctk.StringVar()             # Pour la recherche textuelle
            self.statut_filter_var = ctk.StringVar(value="tous")  # Pour filtrer les résultats de recherche

    # Menu déroulant de tri (en cours / terminée / toutes)
            filtre_frame = ctk.CTkFrame(self, fg_color="transparent")
            filtre_frame.pack(pady=(0, 10))
            ctk.CTkLabel(filtre_frame, text="Filtrer par statut :").pack(side="left", padx=(10, 5))
            ctk.CTkOptionMenu(
            filtre_frame,
            variable=self.tri_var,
            values=["en cours", "terminée", "toutes"],
            command=lambda _: self._refresh()
            ).pack(side="left")

    # Boutons d'action principaux
            top_frame = ctk.CTkFrame(self)
            top_frame.pack(pady=10)

            ctk.CTkButton(top_frame, text="← Retour", command=self._retour_dashboard).grid(row=0, column=0, padx=10)
            ctk.CTkButton(top_frame, text="Exporter en CSV", command=self._export_csv).grid(row=0, column=1, padx=10)
            ctk.CTkButton(top_frame, text="Supprimer", command=self._supprimer_location, fg_color="red", hover_color="darkred").grid(row=0, column=2, padx=10)

    # Barre de recherche
            search_frame = ctk.CTkFrame(self, fg_color="transparent")
            search_frame.pack(pady=(0, 10))

            ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Rechercher par client, véhicule ou statut",
            width=400
            ).grid(row=0, column=0, padx=10)

            ctk.CTkButton(search_frame, text="Rechercher", command=self._rechercher_location).grid(row=0, column=1, padx=5)
            ctk.CTkButton(search_frame, text="Réinitialiser", command=self._reset_recherche, fg_color="gray", hover_color="darkgray").grid(row=0, column=2, padx=5)

            ctk.CTkLabel(search_frame, text="Filtrer résultats :").grid(row=0, column=3, padx=(20, 5))
            ctk.CTkOptionMenu(
            search_frame,
            values=["tous", "en cours", "terminée"],
            variable=self.statut_filter_var
        ).grid(row=0, column=4, padx=5)

    # Zone d’affichage des résultats
            self.table_frame = ctk.CTkScrollableFrame(self, width=750, height=500) 
            
            self.table_frame.pack(pady=10, fill="both", expand=True)

    # Chargement initial des données
            self._load_locations()

    def _load_locations(self):
        db = SessionLocal()
        try:
            filtre = self.tri_var.get() 
            query = db.query(Location).options( joinedload(Location.client), joinedload(Location.vehicule) )

            if filtre == "en cours":
                query = query.filter_by(statut="en cours")
            elif filtre == "terminée":
                query = query.filter_by(statut="terminée")

            locations = query.all()
            self._afficher_locations(locations)
        finally:
            db.close()

    def _afficher_locations(self, locations):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not locations:
            ctk.CTkLabel(
                self.table_frame,
                text="Aucune location trouvée.",
                font=ctk.CTkFont(size=16, slant="italic")
            ).pack(pady=20)
            return

        self.resultats = []

        for loc in locations:
            # print(f"Affichage location ID: {loc.id}")
            client = getattr(loc, "client", None)
            vehicule = getattr(loc, "vehicule", None)

            client_nom = getattr(client, "nom", "Inconnu")
            client_prenom = getattr(client, "prenom", "")
            client_email = getattr(client, "email", "—")

            vehicule_marque = getattr(vehicule, "marque", "Inconnu")
            vehicule_modele = getattr(vehicule, "modele", "")
            vehicule_immat = getattr(vehicule, "immatriculation", "—")

            duree = getattr(loc, "duree", "?")
            statut = getattr(loc, "statut", "en cours").capitalize()

            label = f"{client_nom} {client_prenom} → {vehicule_marque} {vehicule_modele} ({vehicule_immat}) | {duree} j | {statut}"

            self.resultats.append({
                "Client": f"{client_nom} {client_prenom}",
                "Email": client_email,
                "Véhicule": f"{vehicule_marque} {vehicule_modele}",
                "Immatriculation": vehicule_immat,
                "Durée (jours)": duree,
                "Statut": statut
            })

            ligne = ctk.CTkFrame(self.table_frame)
            ligne.pack(fill="x", padx=20, pady=5)

            ctk.CTkRadioButton(
                ligne,
                text=label,
                variable=self.selected_location_id,
                value=str(loc.id),
                width=700
            ).pack(side="left", padx=10)

            if statut.lower() == "en cours":
                ctk.CTkButton(
                    ligne,
                    text="Rendre",
                    command=lambda l=loc: self._rendre_location(l.id),
                    fg_color="orange",
                    hover_color="darkorange"
                ).pack(side="right", padx=10)

    def _rendre_location(self, location_id):
        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment rendre ce véhicule ?"):
            return
        db = SessionLocal()
        location = db.query(Location).filter_by(id=location_id).first()
        if location and hasattr(location, "statut"):
            location.statut = "terminée"
            db.commit()
        db.close()
        self._refresh()

    def _supprimer_location(self):
        location_id = self.selected_location_id.get()
        if not location_id:
            messagebox.showwarning("Aucune location sélectionnée", "Veuillez sélectionner une location à supprimer.")
            return

        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette location ?"):
            return

        db = SessionLocal()
        location = db.query(Location).filter_by(id=int(location_id)).first()
        if location:
            db.delete(location)
            db.commit()
            messagebox.showinfo("Succès", "Location supprimée avec succès.")
            self._load_locations()
        else:
            messagebox.showerror("Erreur", "Location introuvable.")
        db.close()

    def _rechercher_location(self):
        db = SessionLocal()
        query = self.search_var.get().strip().lower()

        locations = db.query(Location).options( joinedload(Location.client), joinedload(Location.vehicule) ).join(Client).join(Vehicule).filter( 
            or_( Client.nom.ilike(f"%{query}%"), 
                Client.prenom.ilike(f"%{query}%"), 
                Client.email.ilike(f"%{query}%"), Vehicule.marque.ilike(f"%{query}%"), 
                Vehicule.modele.ilike(f"%{query}%"), 
                Vehicule.immatriculation.ilike(f"%{query}%"), Location.duree.cast(String).ilike(f"%{query}%"), 
                
                Location.statut.ilike(f"%{query}%")
                #Location.active.cast(String).ilike(f"%{query}%") 
                ) )

        statut = self.statut_filter_var.get().lower()
        if statut in ["en cours", "terminée"]:
            locations = locations.filter(Location.statut == statut)
        
        else: 
            pass

        results = locations.all()
        db.close()

        self._afficher_locations(results)
        messagebox.showinfo("Recherche terminée", f"{len(results)} résultat(s) trouvé(s).")

    def _reset_recherche(self):
        self.search_var.set("")
        self._load_locations()

    def _export_csv(self):
        if not hasattr(self, "resultats") or not self.resultats:
            messagebox.showwarning("Aucun résultat", "Aucune donnée à exporter.")
            return

        filepath = asksaveasfilename(defaultextension=".csv", filetypes=[("Fichier CSV", "*.csv")])
        if not filepath:
            return

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.resultats[0].keys())
            writer.writeheader()
            writer.writerows(self.resultats)

        messagebox.showinfo("Export réussi", f"Les données ont été exportées vers :\n{filepath}")

    def _retour_dashboard(self):
        self.destroy()
        from ui.dashboard_admin import AdminDashboard
        AdminDashboard(self.master)

    def _refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()

    def _fermer(self):
        if self.on_close:
            self.on_close()
        self.destroy()    