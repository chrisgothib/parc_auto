import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Location, Vehicule
from datetime import datetime

class MesLocationsFrame(ctk.CTkFrame):
    def __init__(self, master=None, client=None):
        super().__init__(master)
        self.client = client
        self.tri_var = ctk.StringVar(value="Date décroissante")  # ✅ Initialisée ici
        self._build_ui()
        self._charger_locations()  # ✅ Appelée après l'initialisation

    def _build_ui(self):
        ctk.CTkLabel(self, text="📄 Mes locations", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        tri_options = ["Date décroissante", "Date croissante", "Prix croissant", "Prix décroissant"]
        tri_frame = ctk.CTkFrame(self)
        tri_frame.pack(pady=(0, 10))

        ctk.CTkLabel(tri_frame, text="Trier par :").pack(side="left", padx=10)
        ctk.CTkOptionMenu(tri_frame, variable=self.tri_var, values=tri_options, command=lambda _: self._refresh()).pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _charger_locations(self):
        db = SessionLocal()
        query = db.query(Location).filter_by(client_id=self.client.id)

        tri = self.tri_var.get()
        if tri == "Date croissante":
            query = query.order_by(Location.date_debut.asc())
        elif tri == "Date décroissante":
            query = query.order_by(Location.date_debut.desc())
        elif tri == "Prix croissant":
            query = query.order_by(Location.prix_total.asc())
        elif tri == "Prix décroissant":
            query = query.order_by(Location.prix_total.desc())

        locations = query.all()

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not locations:
            ctk.CTkLabel(self.scroll_frame, text="Aucune location trouvée.", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=20)
        else:
            for loc in locations:
                vehicule = db.query(Vehicule).filter_by(id=loc.vehicule_id).first()
                bloc = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
                bloc.pack(pady=10, fill="x", padx=10)

                infos = f"🚗 {vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})\n"
                infos += f"📅 Du {loc.date_debut.strftime('%d/%m/%Y')} au {loc.date_fin.strftime('%d/%m/%Y')}\n"
                infos += f"💰 Prix total : {loc.prix_total} FCFA"

                ctk.CTkLabel(bloc, text=infos, justify="left").pack(padx=10, pady=10)

                if loc.date_debut > datetime.now():
                    ctk.CTkButton(
                        bloc,
                        text="Annuler",
                        fg_color="red",
                        hover_color="darkred",
                        command=lambda l=loc: self._annuler_location(l)
                    ).pack(pady=(0, 10))

        db.close()

    def _annuler_location(self, location):
        confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment annuler cette location ?")
        if not confirm:
            return

        db = SessionLocal()
        loc = db.query(Location).filter_by(id=location.id).first()
        if loc:
            db.delete(loc)
            db.commit()
            messagebox.showinfo("Succès", "Location annulée avec succès.")
            self._refresh()
        else:
            messagebox.showerror("Erreur", "Location introuvable.")
        db.close()

    def _refresh(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._charger_locations()
