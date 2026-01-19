import customtkinter as ctk
from tkinter import messagebox
from core.database import SessionLocal
from core.models import Vehicule, Voiture, Moto

class ModifierVehicule(ctk.CTkToplevel):
    def __init__(self, master=None, vehicule_id=None, on_success=None):
        super().__init__(master)
        self.title("Modifier un véhicule")
        self.geometry("420x550")
        self.resizable(True, True)
        self.state("zoomed")
        self.vehicule_id = vehicule_id
        self.on_success = on_success
        self.db = SessionLocal()
        self._build_ui()

    def _build_ui(self):
        vehicule = self.db.query(Vehicule).filter_by(id=self.vehicule_id).first()
        if not vehicule:
            messagebox.showerror("Erreur", "Véhicule introuvable.")
            self.destroy()
            return

        self.type = vehicule.type
        self.marque_var = ctk.StringVar(value=vehicule.marque)
        self.modele_var = ctk.StringVar(value=vehicule.modele)
        self.immat_var = ctk.StringVar(value=vehicule.immatriculation)
        self.dispo_var = ctk.StringVar(value="Oui" if vehicule.disponibilite else "Non")
        self.spec_var = ctk.StringVar()

        if self.type == "voiture":
            self.spec_var.set(str(vehicule.nb_portes))
        elif self.type == "moto":
            self.spec_var.set(str(vehicule.cylindree))

        ctk.CTkLabel(self, text="Modifier un véhicule", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        for label, var in [("Marque", self.marque_var), ("Modèle", self.modele_var), ("Immatriculation", self.immat_var)]:
            ctk.CTkLabel(self, text=label).pack(pady=(10, 0))
            ctk.CTkEntry(self, textvariable=var, width=250).pack()

        ctk.CTkLabel(self, text="Disponible").pack(pady=(10, 0))
        ctk.CTkOptionMenu(self, values=["Oui", "Non"], variable=self.dispo_var).pack()

        self.spec_label = ctk.CTkLabel(self, text="Nombre de portes" if self.type == "voiture" else "Cylindrée (cm³)")
        self.spec_label.pack(pady=(15, 0))
        self.spec_entry = ctk.CTkEntry(self, textvariable=self.spec_var, width=250)
        self.spec_entry.pack()

        ctk.CTkButton(self, text="Enregistrer", command=self._modifier, width=200).pack(pady=(30, 10))
        ctk.CTkButton(self, text="Annuler", command=self.destroy, fg_color="gray", hover_color="darkgray", width=200).pack()

    def _modifier(self):
        marque = self.marque_var.get().strip()
        modele = self.modele_var.get().strip()
        immat = self.immat_var.get().strip()
        dispo = self.dispo_var.get() == "Oui"
        spec = self.spec_var.get().strip()

        if not marque or not modele or not immat or not spec:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
            return

        try:
            vehicule = self.db.query(Vehicule).filter_by(id=self.vehicule_id).first()
            vehicule.marque = marque
            vehicule.modele = modele
            vehicule.immatriculation = immat
            vehicule.disponibilite = dispo

            if self.type == "voiture":
                vehicule.nb_portes = int(spec)
            elif self.type == "moto":
                vehicule.cylindree = int(spec)

            self.db.commit()
            messagebox.showinfo("Succès", "Véhicule modifié avec succès.")
            self.destroy()
            if self.on_success:
                self.on_success()
        except ValueError:
            messagebox.showerror("Erreur", "Le champ spécifique doit être un nombre.")

    def destroy(self):
        self.db.close()
        super().destroy()
