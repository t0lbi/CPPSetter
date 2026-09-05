import json
import tkinter as tk
from src.core import *
import time
from threading import Timer
from src.ui.llm_api_tab import open_ai_dialog
from .latex_preview import LatexTab

class ProblemTab:
    def __init__(self, parent, main):
        self.main = main
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.areas = []
        self.json_name = []
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
        self.latex_preview = LatexTab(self.latex_frame, self.main)
        ai_frame = tk.Frame(self.info_frame, bg="#333333")
        ai_frame.pack(fill="x", padx=6, pady=(6, 2))
        tk.Button(
            ai_frame,
            text="AI",
            bg="#3c3f41",
            fg="#ffffff",
            font=("Arial", 11),
            width=8,
            command=self.ask_ai
        ).pack(side="right")
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
        self.json_name = json_name
        def on_text_change(*args):
            if hasattr(self, '_timer'): 
                self._timer.cancel()
            self._timer = Timer(0.5, update)
            self._timer.start()
        def update():
            meta = read_metadata()
            for i in range(len(json_name)):
                meta[json_name[i]] = areas[i].get("1.0", "end")[:-1]
            write_metadata(meta)
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
            val = json_data.get(json_name[i], "")
            areas[i].insert("1.0", str(val))
            labels[i].pack(pady=(3, 6),anchor="w",padx=3)
            areas[i].pack(fill="x", padx=6, pady=(0, 10))
            areas[i].bind("<KeyRelease>", on_text_change)
        self.areas = areas
    def update_ui(self):
        json_data = read_metadata()
        for i in range(len(self.json_name)):
            self.areas[i].delete("1.0", tk.END)
            val = json_data.get(self.json_name[i], "")
            self.areas[i].insert("1.0", str(val))
        if hasattr(self, "latex_preview"):
            self.latex_preview.update_ui()

    def ask_ai(self):
        def wrapper(user_prompt):
            return (
                "You are an assistant for competitive programming problem creation.\n"
                "User request:\n" + user_prompt + "\n\n"
                "Generate problem details strictly formatted as a valid JSON object with EXACTLY these keys:\n"
                "{\n"
                '  "title": "Problem Title",\n'
                '  "description": "Full problem description...",\n'
                '  "input": "Input format description...",\n'
                '  "output": "Output format description...",\n'
                '  "solution": "Solution approach / description...",\n'
                '  "constraints": "Constraints specification...",\n'
                '  "time_limit": "2.0",\n'
                '  "memory_limit": "256.0"\n'
                "}\n"
                "Do not include explanations or markdown code fences. Return only the raw JSON object."
            )

        def on_success(res_text):
            import re
            first_brace = res_text.find("{")
            last_brace = res_text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                res_text = res_text[first_brace:last_brace+1]
            try:
                data = json.loads(res_text)
            except Exception:
                cleaned = re.sub(r",\s*([\]}])", r"\1", res_text)
                data = json.loads(cleaned)
            meta = read_metadata()
            for k in self.json_name:
                if k in data:
                    meta[k] = str(data[k])
            os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
            write_metadata(meta)
            self.update_ui()

        open_ai_dialog(
            self.frame,
            "AI Problem Assistant",
            "Enter prompt to generate/update problem details:",
            wrapper,
            on_success
        )