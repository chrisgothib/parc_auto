import customtkinter as ctk
from style import init_theme
from PIL import Image, ImageTk
from customtkinter import CTkImage
from tkinter import messagebox
import signal
import sys
import os

from core.database import init_db
init_db()

sys.path.append(os.path.abspath("."))
init_theme()

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Système de Location de Véhicules")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.state("zoomed")
        self.configure(padx=40, pady=40)
        self._build_home_page()

    def _build_home_page(self):
        # Titre principal
        title = ctk.CTkLabel(self, text="SYSTÈME DE LOCATION DE VÉHICULES",
                             font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(10, 20))

        # Logo
        try:
            logo_path = os.path.join("assets", "logo.png")
            image = Image.open(logo_path)
            self.logo_img = CTkImage(light_image=image, size=(160, 160))
            ctk.CTkLabel(self, image=self.logo_img, text="").pack()
        except Exception as e:
            print("Erreur chargement logo :", e)
            fallback = ctk.CTkLabel(self, text="(Logo manquant)", font=ctk.CTkFont(size=14, slant="italic"))
            fallback.pack(pady=(0, 20))

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        admin_btn = ctk.CTkButton(btn_frame, text="Administration (Agence)",
                                  width=220, height=50,
                                  font=ctk.CTkFont(size=16, weight="bold"),
                                  command=self.launch_admin)

        client_btn = ctk.CTkButton(btn_frame, text="Client",
                                   width=220, height=50,
                                   font=ctk.CTkFont(size=16),
                                   command=self.launch_client)

        admin_btn.grid(row=0, column=0, padx=20, pady=10)
        client_btn.grid(row=0, column=1, padx=20, pady=10)

    def launch_admin(self):
        from ui.login_admin import AdminLogin
        self.withdraw()
        AdminLogin(self, on_success=self.open_admin_dashboard)

    def launch_client(self):
        from ui.connexion_client import ConnexionClient
        self.withdraw()
        ConnexionClient(self, on_success=lambda client: self.open_client_dashboard(client))

    def open_admin_dashboard(self):
        from ui.dashboard_admin import AdminDashboard
        AdminDashboard(self)

    def open_client_dashboard(self, client):
        from ui.client_dashboard import ClientDashboard
        ClientDashboard(self, client=client)

    def show_home(self):
        self.deiconify()

    def handle_exit(sig, frame):
        print("Fermeture de l'application...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
