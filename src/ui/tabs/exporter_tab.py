import tkinter as tk
from tkinter import ttk

class ExporterTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent, bg="#333333")
        
        self._build_ui()
        
    def _build_ui(self):
        tk.Label(
            self.frame,
            text="Target Platform:",
            bg="#333333",
            fg="#ffffff",
            font=("Arial", 30)
        ).pack(pady=(150,0))
        platforms=["Codeforces", "CMS", "Algoleague"]
        self.platforms_combo = ttk.Combobox(self.frame, values=platforms, state="readonly", font=("Arial", 25))
        self.platforms_combo.pack(pady=75)
        self.platforms_combo.bind("<<ComboboxSelected>>", self.yap)
        


        self.export_button = tk.Button(
            self.frame,
            text="Export to...",
            font=("Arial",25),
            width=15,
            height=3,
            bg="#3c3f41",
            fg="#ffffff",
            command=self.yap
        )
        self.export_button.pack()

    def yap(*args):
        print("hicbir ise yaramiyorum :(")
    def update_ui(self):
        print("Expowdew Dab")