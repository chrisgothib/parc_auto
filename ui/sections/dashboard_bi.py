import customtkinter as ctk
from core.mongoconfig import get_mongo_db
from style import get_color_for_kpi_change

class AdminBIPage(ctk.CTkToplevel):
    def __init__(self, master=None, on_close=None):
        super().__init__(master)
        self.title("Tableau de bord BI")
        self.geometry("1200x800")
        self.configure(fg_color="#101216")
        self.on_close = on_close

        self.previous_ca = 0
        self._build_layout()
        self.refresh()

    def _build_layout(self):
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self, fg_color="#151a22")
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.header.columnconfigure((0, 1, 2), weight=1)

        self.label_ca = self._kpi_card(self.header, 0, "Chiffre d'affaires", "0 FCFA")
        self.label_nb = self._kpi_card(self.header, 1, "Nombre de locations", "0")
        self.label_dm = self._kpi_card(self.header, 2, "Durée moyenne (jours)", "0")

        self.main = ctk.CTkFrame(self, fg_color="#151a22")
        self.main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main.rowconfigure((0, 1), weight=1)
        self.main.columnconfigure((0, 1), weight=1)

        self._chart_block(self.main, 0, 0, "CA par mois")
        self._chart_block(self.main, 0, 1, "CA par région")
        self._chart_block(self.main, 1, 0, "Évolution des KPI")
        self._chart_block(self.main, 1, 1, "Taux d’occupation")

        self.sidebar = ctk.CTkFrame(self, fg_color="#151a22")
        self.sidebar.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Filtres",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        self.filter_region = ctk.CTkComboBox(self.sidebar,
                                             values=["Toutes", "Littoral", "Centre", "Nord"],
                                             width=200)
        self.filter_region.pack(pady=5)

        self.filter_type = ctk.CTkComboBox(self.sidebar,
                                           values=["Tous", "voiture", "moto"],
                                           width=200)
        self.filter_type.pack(pady=5)

        self.btn_refresh = ctk.CTkButton(self.sidebar, text="Actualiser", command=self.refresh)
        self.btn_refresh.pack(pady=10)

        self.btn_retour = ctk.CTkButton(self.sidebar, text="⬅ Retour", command=self._retour)
        self.btn_retour.pack(pady=(30, 10))

    def _kpi_card(self, parent, col, title, value):
        frame = ctk.CTkFrame(parent, fg_color="#22324d")
        frame.grid(row=0, column=col, sticky="nsew", padx=8, pady=8)

        ctk.CTkLabel(frame, text=title,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))

        label = ctk.CTkLabel(frame, text=value,
                             font=ctk.CTkFont(size=22, weight="bold"))
        label.pack(anchor="w", padx=10, pady=(0, 10))
        return label

    def _chart_block(self, parent, r, c, title):
        frame = ctk.CTkFrame(parent, fg_color="#1d2633")
        frame.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)

        ctk.CTkLabel(frame, text=title,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=8)

        ctk.CTkLabel(frame, text="Graphique à venir...",
                     font=ctk.CTkFont(size=12, slant="italic")).pack(expand=True)

        return frame

    def refresh(self):
        mongo = get_mongo_db()
        data = mongo.kpi_dashboard.find_one() or {}
        global_kpi = data.get("global", {})

        ca = global_kpi.get("chiffre_affaires", 0)
        nb = global_kpi.get("nb_locations", 0)
        dm = global_kpi.get("duree_moyenne_jours", 0)

        delta_ca = ca - self.previous_ca
        self.previous_ca = ca

        self.label_ca.configure(
            text=f"{int(ca)} FCFA",
            text_color=get_color_for_kpi_change(delta_ca)
        )
        self.label_nb.configure(text=str(int(nb)))
        self.label_dm.configure(text=str(dm))

    def _retour(self):
        self.destroy()
        if self.on_close:
            self.on_close()
