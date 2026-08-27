import tkinter as tk
from src.core import write_metadata, read_metadata
import time
from threading import Timer

class ProblemTab:
    def __init__(self, parent, main):
        self.main = main
        self.parent = parent
        self.frame = tk.Frame(parent)
        self._build_ui()
    def _build_ui(self):
        self.paned_window = tk.PanedWindow(
            self.frame,
            orient="horizontal",
            sashrelief="raised",
            sashwidth=5
        )
        self.paned_window.pack(fill="both", expand=True)
        self.info_frame = tk.Frame(self.paned_window, width=150, bg="#333333")
        self.latex_frame = tk.Frame(self.paned_window, bg="#111111")
        self.paned_window.add(self.info_frame, minsize=50)
        self.paned_window.add(self.latex_frame, minsize=50)
        labels = []
        areas = []
        label_texts = [
            "Title:",
            "Problem Description:",
            "Input Format:",
            "Output Format:",
            "Solution Description (optional):",
            "Constraints:",
            "Time limit (sec):",
            "Memory Limit (MB):"
        ]
        heights = [1,4,3,3,4,3,1,1]
        json_name = [
            "title", 
            "description", 
            "input", 
            "output", 
            "solution", 
            "constraints", 
            "time_limit", 
            "memory_limit"
        ]
        def on_text_change(*args):
            if hasattr(self, '_timer'): 
                self._timer.cancel()
            self._timer = Timer(0.5, update)
            self._timer.start()
        def update():
            write_metadata({
                json_name[0]: areas[0].get("1.0","end")[:-1],
                json_name[1]: areas[1].get("1.0","end")[:-1],
                json_name[2]: areas[2].get("1.0","end")[:-1],
                json_name[3]: areas[3].get("1.0","end")[:-1],
                json_name[4]: areas[4].get("1.0","end")[:-1],
                json_name[5]: areas[5].get("1.0","end")[:-1],
                json_name[6]: areas[6].get("1.0","end")[:-1],
                json_name[7]: areas[7].get("1.0","end")[:-1],
            })
        for i in range(8):
            labels.append(
                tk.Label(
                    self.info_frame,
                    text=label_texts[i],
                    font=("Arial", 11),
                    bg="#333333",
                    fg="#ffffff"
                )
            )
            areas.append(
                tk.Text(
                    self.info_frame,
                    height=heights[i],
                    wrap="word", 
                    font=("Arial", 12),
                    bg="#111111",
                    fg="#ffffff"
                )
            )
            json_data = read_metadata()
            areas[i].insert("1.0", json_data[json_name[i]])
            labels[i].pack(pady=(3, 6),anchor="w",padx=3)
            areas[i].pack(fill="x", padx=6, pady=(0, 10))
            areas[i].bind("<KeyRelease>", on_text_change)
    def update_ui(self):
        print("Pwoblem Dab")