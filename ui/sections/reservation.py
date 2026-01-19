# packages_customer/ui/sections/reservation.py

import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from core.database import SessionLocal
from core.models import Vehicule, Location


class ReservationFrame(ctk.CTkFrame):
    def __init__(self, master, client, **kwargs):
        super().__init__(master, **kwargs)
        self.client = client
        self.selection_vehicules = []
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="🗓️ Nouvelle réservation", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # Sélection des dates
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(pady=10)

        ctk.CTkLabel(date_frame, text="Date de début :").grid(row=0, column=0, padx=5)
        self.date_debut = DateEntry(date_frame, date_pattern="yyyy-mm-dd")
        self.date_debut.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(date_frame, text="Date de fin :").grid(row=0, column=2, padx=5)
        self.date_fin = DateEntry(date_frame, date_pattern="yyyy-mm-dd")
        self.date_fin.grid(row=0, column=3, padx=5)

        ctk.CTkButton(self, text="🔍 Rechercher les véhicules disponibles", command=self._rechercher_vehicules).pack(pady=10)

        # Zone d’affichage des véhicules
        self.vehicules_frame = ctk.CTkScrollableFrame(self)
        self.vehicules_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Boutons de validation
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="Valider la réservation", command=self._valider_reservation).grid(row=0, column=0, padx=10)
        ctk.CTkButton(action_frame, text="Annuler", command=self._reset).grid(row=0, column=1, padx=10)

    def _rechercher_vehicules(self):
        db = SessionLocal()
        debut = self.date_debut.get_date()
        fin = self.date_fin.get_date()

        if debut >= fin:
            messagebox.showwarning("Erreur", "La date de fin doit être postérieure à la date de début.")
            db.close()
            return

        # Exclure les véhicules déjà loués sur cette période
        sous_requete = db.query(Location.vehicule_id).filter(
            Location.date_debut <= fin,
            Location.date_fin >= debut,
            Location.statut == "en cours"
        )

        vehicules = db.query(Vehicule).filter(~Vehicule.id.in_(sous_requete)).all()
        db.close()

        self._afficher_vehicules(vehicules)

    def _afficher_vehicules(self, vehicules):
        for widget in self.vehicules_frame.winfo_children():
            widget.destroy()
        self.selection_vehicules = []

        if not vehicules:
            ctk.CTkLabel(self.vehicules_frame, text="Aucun véhicule disponible pour cette période.").pack(pady=20)
            return

        for v in vehicules:
            frame = ctk.CTkFrame(self.vehicules_frame)
            frame.pack(fill="x", pady=5, padx=10)

            var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                frame,
                text=f"{v.marque} {v.modele} ({v.immatriculation}) - {v.prix_journalier} FCFA/jour",
                variable=var
            ).pack(side="left")
            self.selection_vehicules.append((v, var))

    def _valider_reservation(self):
        db = SessionLocal()
        debut = self.date_debut.get_date()
        fin = self.date_fin.get_date()
        duree = (fin - debut).days

        if duree <= 0:
            messagebox.showwarning("Erreur", "La durée de location doit être d'au moins un jour.")
            db.close()
            return

        count = 0
        for vehicule, var in self.selection_vehicules:
            if var.get():
                if vehicule.prix_journalier is None:
                    messagebox.showerror("Erreur", f"Le véhicule {vehicule.marque} {vehicule.modele} n'a pas de prix défini.")
                    continue
                location = Location(
                    client_id=self.client.id,
                    vehicule_id=vehicule.id,
                    date_debut=debut,
                    date_fin=fin,
                    duree=duree,

                    prix_total=int(vehicule.prix_journalier) * duree,
                    statut="en cours"
                )
                db.add(location)
                db.flush()  # pour obtenir l'ID avant le commit

                # ✅ Appel immédiat de l’événement BI
                from etl.insert_event import log_rental_created
                log_rental_created(location.id)
                count += 1

        if count == 0:
            messagebox.showwarning("Aucun véhicule sélectionné", "Veuillez sélectionner au moins un véhicule.")
            db.close()
            return

        db.commit()
        db.close()
        messagebox.showinfo("Succès", f"{count} réservation(s) enregistrée(s).")
        self._reset()

    def _reset(self):
        for widget in self.vehicules_frame.winfo_children():
            widget.destroy()
        self.selection_vehicules = []
