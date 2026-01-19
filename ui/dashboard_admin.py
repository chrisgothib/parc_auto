import customtkinter as ctk
from tkinter import messagebox
from ui.vehicules import VehiculeManager
from ui.clients import ClientManager
from ui.locations import LocationManager
from ui.sections.dashboard_bi import AdminBIPage  # ✅ Nouveau module BI

class AdminDashboard(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Tableau de bord - Administration")
        self.geometry("800x600")
        self.resizable(True, True)
        self.state("zoomed")
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # En-tête
        ctk.CTkLabel(self, text="Connecté : admin", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 10))

        # Boutons de navigation
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=40)

        ctk.CTkButton(btn_frame, text="🚗 Gestion des véhicules", width=300, height=50,
                      font=ctk.CTkFont(size=16), command=self.open_vehicules).pack(pady=10)

        ctk.CTkButton(btn_frame, text="👤 Gestion des clients", width=300, height=50,
                      font=ctk.CTkFont(size=16), command=self.open_clients).pack(pady=10)

        ctk.CTkButton(btn_frame, text="📄 Gestion des locations", width=300, height=50,
                      font=ctk.CTkFont(size=16), command=self.open_locations).pack(pady=10)

        # ✅ Nouveau bouton BI
        ctk.CTkButton(btn_frame, text="📊 Tableau de bord BI", width=300, height=50,
                      font=ctk.CTkFont(size=16), command=self.open_bi_dashboard).pack(pady=(30, 10))

        # Bouton de déconnexion
        logout_btn = ctk.CTkButton(self, text="🚪 Déconnexion", command=self._logout)
        logout_btn.pack(pady=10)

    def open_vehicules(self):
        self.withdraw()
        VehiculeManager(self, on_close=self._reafficher_dashboard)

    def open_clients(self):
        self.withdraw()
        ClientManager(self, on_close=self._reafficher_dashboard)

    def open_locations(self):
        self.withdraw()
        LocationManager(self, on_close=self._reafficher_dashboard)

    def open_bi_dashboard(self):
        self.withdraw()
        AdminBIPage(self, on_close=self._reafficher_dashboard)

    def _logout(self):
        from core.session import Session
        from ui.login_admin import AdminLogin
        Session.current_user = None
        self.destroy()
        AdminLogin(self.master)

    def _reafficher_dashboard(self):
        self.deiconify()
