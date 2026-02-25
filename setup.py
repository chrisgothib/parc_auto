from cx_Freeze import setup, Executable
import sys
import os

# Inclure les fichiers nécessaires (ex: images, fichiers de config, etc.)
includefiles = []

# Définir la base pour Windows GUI
base = None
if sys.platform == "win32":
    base = "gui"  # évite d'ouvrir une console noire

# Configuration du setup
setup(
    name="ParcAuto",
    version="1.0",
    description="Application de tableau de bord BI pour agence de location",
    options={
        "build_exe": {
            "packages": ["os", "sys", "customtkinter", "matplotlib", "numpy", "transformers", "core"],
            "include_files": includefiles,
            "excludes": ["tkinter.test", "unittest", "email", "html", "http", "xml", "pydoc_data"]
        }
    },
    executables=[Executable("main.py", base=base, target_name="ParcAuto.exe")]
)
