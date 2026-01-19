import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Voiture, Moto

class AjouterVehicule(ctk.CTkToplevel):
    def __init__(self, master=None, on_success=None):
        super().__init__(master)
        self.title("Ajouter un véhicule")
        self.geometry("500x600")
        self.resizable(True, True)
        self.state("zoomed")
        self.on_success = on_success
        self.db = SessionLocal()
        self._build_ui()

    def _build_ui(self):
        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Variables
        self.type_var = ctk.StringVar(value="Voiture")
        self.marque_var = ctk.StringVar()
        self.modele_var = ctk.StringVar()
        self.immat_var = ctk.StringVar()
        self.dispo_var = ctk.StringVar(value="Oui")
        self.spec_var = ctk.StringVar()
        self.prix_var = ctk.StringVar()

        # Titre
        ctk.CTkLabel(self.scroll_frame, text="Ajouter un véhicule", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        # Type de véhicule
        ctk.CTkLabel(self.scroll_frame, text="Type").pack(pady=(5, 0))
        ctk.CTkOptionMenu(self.scroll_frame, values=["Voiture", "Moto"], variable=self.type_var, command=self._update_spec_field).pack()

        # Champs communs
        for label, var in [("Marque", self.marque_var), ("Modèle", self.modele_var), ("Immatriculation", self.immat_var)]:
            ctk.CTkLabel(self.scroll_frame, text=label).pack(pady=(10, 0))
            ctk.CTkEntry(self.scroll_frame, textvariable=var, width=250).pack()

        # Disponibilité
        ctk.CTkLabel(self.scroll_frame, text="Disponible").pack(pady=(10, 0))
        ctk.CTkOptionMenu(self.scroll_frame, values=["Oui", "Non"], variable=self.dispo_var).pack()

        # Champ spécifique
        self.spec_label = ctk.CTkLabel(self.scroll_frame, text="Nombre de portes")
        self.spec_label.pack(pady=(15, 0))
        self.spec_entry = ctk.CTkEntry(self.scroll_frame, textvariable=self.spec_var, width=250)
        self.spec_entry.pack()

        # Prix journalier
        ctk.CTkLabel(self.scroll_frame, text="Prix journalier (FCFA) :").pack(pady=(10, 0))
        ctk.CTkEntry(self.scroll_frame, textvariable=self.prix_var, width=250).pack()

        # Boutons
        ctk.CTkButton(self.scroll_frame, text="Ajouter", command=self._ajouter, width=200).pack(pady=(30, 10))
        ctk.CTkButton(self.scroll_frame, text="Annuler", command=self.destroy, fg_color="gray", hover_color="darkgray", width=200).pack()

    def _update_spec_field(self, selected_type):
        if selected_type == "Voiture":
            self.spec_label.configure(text="Nombre de portes")
        else:
            self.spec_label.configure(text="Cylindrée (cm³)")
        self.spec_var.set("")

    def _ajouter(self):
        type_vehicule = self.type_var.get()
        marque = self.marque_var.get().strip()
        modele = self.modele_var.get().strip()
        immat = self.immat_var.get().strip()
        dispo = self.dispo_var.get() == "Oui"
        spec = self.spec_var.get().strip()
        prix_str = self.prix_var.get().strip()

        if not prix_str.isdigit():
            messagebox.showerror("Erreur", "Veuillez entrer un prix journalier valide.")
            return
        prix = int(prix_str)

        if not marque or not modele or not immat or not spec:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
            return

        if self.db.query(Voiture).filter_by(immatriculation=immat).first() or \
           self.db.query(Moto).filter_by(immatriculation=immat).first():
            messagebox.showerror("Erreur", "Cette immatriculation existe déjà.")
            return

        try:
            if type_vehicule == "Voiture":
                vehicule = Voiture(
                    marque=marque,
                    modele=modele,
                    immatriculation=immat,
                    nb_portes=int(spec),
                    disponibilite=dispo,
                    prix_journalier=prix,
                    type="voiture"
                )
            else:
                vehicule = Moto(
                    marque=marque,
                    modele=modele,
                    immatriculation=immat,
                    cylindree=int(spec),
                    disponibilite=dispo,
                    prix_journalier=prix,
                    type="moto"
                )
        except ValueError:
            messagebox.showerror("Erreur", "Le champ spécifique doit être un nombre.")
            return

        self.db.add(vehicule)
        self.db.commit()
        messagebox.showinfo("Succès", f"{type_vehicule} {marque} {modele} ajoutée avec succès.")
        self.destroy()
        if self.on_success:
            self.on_success()

    def destroy(self):
        self.db.close()
        super().destroy()
