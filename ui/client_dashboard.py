# ui/client_dashboard.py

import customtkinter as ctk
from ui.sections.mes_infos import MesInfosFrame
from ui.sections.mes_locations import MesLocationsFrame
from ui.sections.reservation import ReservationFrame

class ClientDashboard(ctk.CTkToplevel):
    def __init__(self, master=None, client=None):
        super().__init__(master)
        self.title("Espace Client")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.state("zoomed")
        self.client = client
        self._build_ui()

    def _build_ui(self):
        # Titre
        ctk.CTkLabel(self, text=f"👋 Bonjour {self.client.prenom}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        ctk.CTkButton(self, text="🚪 Déconnexion", command=self._logout).pack(pady=(0, 20))


        # Menu de navigation
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=10)

        ctk.CTkButton(nav_frame, text="Mes informations", command=self._afficher_infos).grid(row=0, column=0, padx=10)
        ctk.CTkButton(nav_frame, text="Mes locations", command=self._afficher_locations).grid(row=0, column=1, padx=10)
        ctk.CTkButton(nav_frame, text="Réserver un véhicule", command=self._afficher_reservation).grid(row=0, column=2, padx=10)

        # Zone de contenu
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(pady=20, fill="both", expand=True)

        self._afficher_infos()

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _afficher_infos(self):
        self._clear_content()
        MesInfosFrame(self.content_frame, client=self.client).pack(fill="both", expand=True)

    def _afficher_locations(self):
        self._clear_content()
        MesLocationsFrame(self.content_frame, client=self.client).pack(fill="both", expand=True)

    def _afficher_reservation(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        ReservationFrame(self.content_frame, client=self.client).pack(fill="both", expand=True)
        


    def _logout(self):
        from core.session import Session
        Session.current_user = None
        self.destroy()
        self.master.show_home()  # ← retour à l’accueil

    
