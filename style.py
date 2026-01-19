import customtkinter as ctk

# Dictionnaire global pour stocker les polices
fonts = {}

def init_theme():
    """
    Initialise le thème global de l'application.
    À appeler avant la création de la fenêtre principale.
    """
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

def define_fonts():
    """
    Crée les polices personnalisées.
    À appeler après la création de la fenêtre principale.
    """
    global fonts
    fonts = {
        "title": ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        "subtitle": ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        "body": ctk.CTkFont(family="Segoe UI", size=14),
        "small": ctk.CTkFont(family="Segoe UI", size=12),
        "kpi": ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
    }

def get_color_for_kpi_change(delta):
    """
    Retourne une couleur en fonction de l’évolution d’un KPI.
    delta > 0 → vert, delta < 0 → rouge, sinon gris.
    """
    if delta > 0:
        return "#22c55e"
    elif delta < 0:
        return "#ef4444"
    else:
        return "#64748b"