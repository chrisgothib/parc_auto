from asyncio import events
import customtkinter as ctk
from transformers import pipeline
from core.mongoconfig import get_mongo_db
from style import get_color_for_kpi_change
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.cm as cm

class AdminBIPage(ctk.CTkToplevel):
    def __init__(self, master=None, on_close=None):
        super().__init__(master)
        self.title("Tableau de bord BI")
        self.geometry("1200x800")
        self.resizable(True, True)
        self.state("zoomed")
        self.configure(fg_color="#101216")
        self.on_close = on_close

        self.previous_ca = 0
        self._build_layout()
        self._charger_filtres_dynamiques()

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

        self.chart_duree_mois = self._chart_block(self.main, 1, 1, "Durée totale louée par mois")
        self.chart_ca_mois = self._chart_block(self.main, 0, 0, "CA par mois")
        
        self.chart_ca_region = self._chart_block(self.main, 0, 1, "CA par région")
        
        self.chart_vehicules_region = self._chart_block(self.main, 1, 0, "Véhicules par région")

        self.chart_nb_locations_mois = self._chart_block(self.main, 1, 0, "Évolution des locations par mois")

        
        



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
        self.filter_vehicule = ctk.CTkComboBox(self.sidebar, values=["Tous"], width=200)
        self.filter_vehicule.pack(pady=5)
        self.filter_vehicule.set("Tous")


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

        

        return frame

    def refresh(self):
        mongo = get_mongo_db()
        collection = mongo.events

        region = self.filter_region.get()
        type_vehicule = self.filter_type.get()
        vehicule_label = self.filter_vehicule.get()

        match_stage = {"event_type": "rental_created", "payload.prix_total": {"$type": "number"}}

        if region != "Toutes":
            try:
                region_int = int(region)
                match_stage["$or"] = [
                    {"payload.region": region},
                    {"payload.region": region_int}
                ]
            except ValueError:
                match_stage["payload.region"] = region


        if type_vehicule != "Tous":
            match_stage["payload.type"] = type_vehicule

        if hasattr(self, "vehicule_label_to_id") and vehicule_label != "Tous":
            vehicule_id = self.vehicule_label_to_id.get(vehicule_label)
            if vehicule_id is not None:
                try:
                    match_stage["payload.vehicule_id"] = int(vehicule_id)
                except ValueError:
                    print(f"[WARN] ID de véhicule invalide : {vehicule_id}")


        pipeline = [{"$match": match_stage}]
        pipeline += [
            {"$group": {
                "_id": None,
                "chiffre_affaires": {"$sum": "$payload.prix_total"},
                "nb_locations": {"$sum": 1},
                "duree_totale_jours": {
                    "$sum": {
                        "$divide": [
                            {"$subtract": [
                                {"$toDate": "$payload.date_fin"},
                                {"$toDate": "$payload.date_debut"}
                            ]},
                            1000 * 60 * 60 * 24
                        ]
                    }
                }
            }},
        {"$addFields": {
            "duree_moyenne_jours": {
                "$cond": [
                    {"$gt": ["$nb_locations", 0]},
                    {"$round": [{"$divide": ["$duree_totale_jours", "$nb_locations"]}, 2]},
                    0
                ]
            }
        }}
    ]

        result = list(collection.aggregate(pipeline))
        global_kpi = result[0] if result else {}

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

        # 🔹 CHIFFRE D’AFFAIRES PAR RÉGION
        pipeline_ca_region = [
            {"$match": match_stage},
            {"$group": {
                "_id": "$payload.region",
                "ca": {"$sum": "$payload.prix_total"}
            }},
            {"$sort": {"ca": -1}}
        ]
        ca_par_region = list(collection.aggregate(pipeline_ca_region))
        labels_ca = [str(doc["_id"]) for doc in ca_par_region]
        valeurs_ca = [doc["ca"] for doc in ca_par_region]
        self._afficher_graphique(self.chart_ca_region, labels_ca, valeurs_ca, "Région", "Chiffre d'affaires")

        # 🔹 NOMBRE DE VÉHICULES PAR RÉGION
        pipeline_vehicules_region = [
            {"$match": match_stage},
            {"$group": {
                "_id": {"region": "$payload.region", "vehicule_id": "$payload.vehicule_id"},
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.region",
                "nb_vehicules": {"$sum": 1}
            }},
            {"$sort": {"nb_vehicules": -1}}
        ]
        vehicules_par_region = list(collection.aggregate(pipeline_vehicules_region))
        labels_vr = [str(doc["_id"]) for doc in vehicules_par_region]
        valeurs_vr = [doc["nb_vehicules"] for doc in vehicules_par_region]
        self._afficher_graphique(self.chart_vehicules_region, labels_vr, valeurs_vr, "Région", "Nombre de véhicules")

        # 🔹 CHIFFRE D’AFFAIRES PAR MOIS
        pipeline_ca_mois = [
            {"$match": match_stage},
            {"$addFields": {
                "mois": {"$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$payload.date_debut"}}}
            }},
            {"$group": {
                "_id": "$mois",
                "ca": {"$sum": "$payload.prix_total"}
            }},
            {"$sort": {"_id": 1}}
    ]
        ca_par_mois = list(collection.aggregate(pipeline_ca_mois))
        labels_mois = [doc["_id"] for doc in ca_par_mois]
        valeurs_mois = [doc["ca"] for doc in ca_par_mois]
        self._afficher_graphique(self.chart_ca_mois, labels_mois, valeurs_mois, "Mois", "Chiffre d'affaires")

        # 🔹 NOMBRE DE LOCATIONS PAR MOIS
        pipeline_nb_mois = [
            {"$match": match_stage},
            {"$addFields": {
                "mois": {"$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$payload.date_debut"}}}
            }},
            {"$group": {
                "_id": "$mois",
                "nb_locations": {"$sum": 1}
         }},
        {"$sort": {"_id": 1}}
        ]
        nb_par_mois = list(collection.aggregate(pipeline_nb_mois))
        labels_nb = [doc["_id"] for doc in nb_par_mois]
        valeurs_nb = [doc["nb_locations"] for doc in nb_par_mois]
        self._afficher_graphique(self.chart_nb_locations_mois, labels_nb, valeurs_nb, "Mois", "Nombre de locations")

        # 🔹 DURÉE TOTALE LOUÉE PAR MOIS
        pipeline_duree_mois = [
            {"$match": match_stage},
            {"$addFields": {
                "mois": {"$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$payload.date_debut"}}},
                "duree_jours": {
                "$divide": [
                    {"$subtract": [
                        {"$toDate": "$payload.date_fin"},
                        {"$toDate": "$payload.date_debut"}
                    ]},
                    1000 * 60 * 60 * 24
                ]
            }
        }},
        {"$group": {
            "_id": "$mois",
            "duree_totale": {"$sum": "$duree_jours"}
        }},
        {"$sort": {"_id": 1}}
    ]
        duree_par_mois = list(collection.aggregate(pipeline_duree_mois))
        labels_duree = [doc["_id"] for doc in duree_par_mois]
        valeurs_duree = [round(doc["duree_totale"], 2) for doc in duree_par_mois]
        self._afficher_graphique(self.chart_duree_mois, labels_duree, valeurs_duree, "Mois", "Jours loués")






    def _charger_filtres_dynamiques(self):
        mongo = get_mongo_db()
        events = mongo.events

        # RÉGIONS (codes ou noms)
        regions_brutes = events.distinct("payload.region")
        regions_brutes = [r for r in regions_brutes if r]
        self.region_values = sorted(set(str(r) for r in regions_brutes))
        self.filter_region.configure(values=["Toutes"] + self.region_values)
        self.filter_region.set("Toutes")

        # TYPES DE VÉHICULES
        types_bruts = events.distinct("payload.type")
        types_bruts = [t for t in types_bruts if t]
        self.type_values = sorted(set(str(t) for t in types_bruts))
        self.filter_type.configure(values=["Tous"] + self.type_values)
        self.filter_type.set("Tous")

        # VÉHICULES (ID → nom lisible)
        vehicule_ids = events.distinct("payload.vehicule_id")
        vehicule_ids = [v for v in vehicule_ids if v is not None]

        from core.database import SessionLocal
        from core.models import Vehicule
        db = SessionLocal()
        vehicules = db.query(Vehicule).filter(Vehicule.id.in_(vehicule_ids)).all()
        db.close()

        self.vehicule_map = {
        str(v.id): f"{v.marque} {v.modele} (ID {v.id})" for v in vehicules
        }
        self.vehicule_label_to_id = {label: vid for vid, label in self.vehicule_map.items()}

        vehicule_labels = sorted(self.vehicule_map.values())
        self.filter_vehicule.configure(values=["Tous"] + vehicule_labels)
        self.filter_vehicule.set("Tous")
    
    

    def _afficher_graphique(self, frame, labels, valeurs, xlabel, ylabel):
        for widget in frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)

        # Convert labels to indices if trop nombreux
        if len(labels) > 30:
            x = np.arange(len(valeurs))
            ax.plot(x, valeurs, color="#4e79a7", linewidth=2)
            ax.set_xticks(np.linspace(0, len(labels)-1, 10, dtype=int))
            ax.set_xticklabels([labels[i] for i in np.linspace(0, len(labels)-1, 10, dtype=int)], rotation=45)
        else:
            x = np.arange(len(valeurs))
            colors = cm.viridis(np.linspace(0, 1, len(valeurs)))
            for i in range(len(valeurs)-1):
                ax.plot(x[i:i+2], valeurs[i:i+2], color=colors[i], linewidth=2)

            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle='--', alpha=0.3)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)



        



    def _retour(self):
        self.destroy()
        if self.on_close:
            self.on_close()
