import tkinter as tk
from tkinter import ttk

class IOTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = ttk.Frame(parent)
        
        self._build_ui()
        
    def _build_ui(self):
        label = tk.Label(self.frame, text="IO Tab", font=("Arial", 16))
        label.pack(pady=50)