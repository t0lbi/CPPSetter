import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from src.core import *
from src.ui.llm_api_tab import open_ai_dialog

class GeneratorsTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self.loaded = []
        self._build_ui()
        
    def _build_ui(self):
        self.main_frame = tk.Frame(self.frame, bg="#333333", width=800)
        self.debug_frame = tk.Frame(self.frame, bg="#333333")
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(side="left", fill="both")
        self.debug_frame.pack(side="right", fill="both", expand=True)


        tk.Label(self.main_frame, text="Name:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        self.gen_name = tk.Text(self.main_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.gen_name.pack(padx=5, pady=5, anchor="w")
        tk.Button(self.main_frame, text="Create New Generator", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.create_gen).pack(anchor="w", padx=5)

        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#111111",
            foreground="#ffffff",
            rowheight=20,
            fieldbackground="#111111",
            bordercolor="#333333",
            borderwidth=1,
            lightcolor="#333333",
            darkcolor="#333333"
        )
        style.configure(
            "Treeview.Heading",
            background="#333333",
            foreground="#ffffff",
            bordercolor="#3c3f41",
            relief="flat",
            font=("TkDefaultFont", 10, "bold")
        )
        columns = (
            "name",
        )
        headings = (
            "Generator Name",
        )
        tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            height=25
        )
        for i in range(len(columns)):
            tree.heading(columns[i], text=headings[i])
            tree.column(columns[i], width=len(headings[i])*15+5, anchor="center", stretch=False)
        tree.pack(padx=20, pady=20, fill="both", expand=True)
        self.tree = tree
        self.tree.bind("<<TreeviewSelect>>", self.on_gen_select)

        gen_frame = tk.Frame(self.main_frame, bg="#333333")
        gen_frame.pack(fill="x", pady=5)
        tk.Button(gen_frame, text="Edit", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.edit_gen).pack(side="left", padx=5)
        tk.Button(gen_frame, text="Upload", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.upload_gen).pack(side="left", padx=5)
        tk.Button(gen_frame, text="AI", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.ask_ai_gen).pack(side="left", padx=5)


        tk.Label(self.main_frame, text="Arguments:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        self.gen_args = tk.Text(self.main_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.gen_args.pack(padx=5, pady=5, anchor="w")
        
        gen_runner_frame = tk.Frame(self.main_frame, bg="#333333")
        gen_runner_frame.pack(fill="x", pady=5)
        tk.Button(gen_runner_frame, text="Run", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.run_current_gen).pack(side="left", padx=5)
        tk.Button(gen_runner_frame, text="View Input", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.view_gen_output).pack(side="left", padx=5)
        
        
        input_area = tk.Label(self.debug_frame,font=("Arial", 11), bg="#111111",fg="#ffffff",text="Errors will be shown here.", anchor="nw", justify="left")
        input_area.pack(padx=20, pady=20, fill="both", expand=True)
        self.input_area = input_area

    def create_gen(self):
        name = self.gen_name.get("1.0", "end")[:-1].strip()
        path, error = create_generator(name)
        if error:
            self.input_area.config(text=error)
            return
        self.input_area.config(text=f"Created {name}")
        self.refresh_generators()

    def refresh_generators(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.loaded = []
        generators = list_generators()
        for gen in generators:
            self.loaded.append(gen)
            self.tree.insert("", tk.END, values=[gen])

    def on_gen_select(self, event=None):
        selected = self.tree.selection()
        if selected:
            item_data = self.tree.item(selected)
            name = str(item_data["values"][0])
            self.gen_name.delete("1.0", tk.END)
            self.gen_name.insert("1.0", name)

    def edit_gen(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_data = self.tree.item(selected)
        name = str(item_data["values"][0])
        path = generator_path(name)
        open_in_gnome_text_editor(path)

    def upload_gen(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        name = self.gen_name.get("1.0", "end")[:-1].strip()
        dest, error = import_generator(path, name if name else None)
        if error:
            self.input_area.config(text=error)
            return
        self.input_area.config(text=f"Imported {dest}")
        self.refresh_generators()

    def run_current_gen(self):
        selected = self.tree.selection()
        if not selected:
            self.input_area.config(text="No generator selected.")
            return
        item_data = self.tree.item(selected)
        name = str(item_data["values"][0])
        args = self.gen_args.get("1.0", "end")[:-1].strip()
        os.makedirs("temp", exist_ok=True)
        gen_cpp = generator_path(name)
        exe_path = f"temp/gen_{name}"
        if os.path.isdir(exe_path):
            shutil.rmtree(exe_path)
        if compile_code(gen_cpp, "none", "", exe_path) != 1:
            err = get_last_compile_error()
            self.input_area.config(text=err if err else "Generator compilation failed (CE).")
            return
        out_path = "temp/gen.out"
        if run_gen(exe_path, args, out_path) != 1:
            self.input_area.config(text="Generator runtime error (RE).")
            return
        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            lines = content.splitlines(keepends=True)
            prefix_20 = "".join(lines[:20])
            cutoff = min(150, len(prefix_20))
            if len(content) > cutoff:
                rem = len(content) - cutoff
                sep = "" if content[:cutoff].endswith("\n") else "\n"
                preview = f"{content[:cutoff]}{sep}...Truncated ({rem} chars)"
            else:
                preview = content
            self.input_area.config(text=preview, justify="left", anchor="nw")
        else:
            self.input_area.config(text="Output file not found.")

    def view_gen_output(self):
        out_path = "temp/gen.out"
        if os.path.isfile(out_path):
            open_in_gnome_text_editor(out_path)
        else:
            self.input_area.config(text="Output file not found.")

    def update_buttons(self, *args):
        pass

    def update_ui(self):
        self.refresh_generators()

    def ask_ai_gen(self):
        selected = self.tree.selection()
        name = ""
        if selected:
            name = str(self.tree.item(selected)["values"][0])
        else:
            name = self.gen_name.get("1.0", "end")[:-1].strip()
        if not name:
            name = "gen1"
            self.gen_name.delete("1.0", tk.END)
            self.gen_name.insert("1.0", name)

        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input Format: {meta.get('input', '')}\n"
                f"Constraints: {meta.get('constraints', '')}\n"
            )
            return (
                "You are an assistant for competitive programming problem setters.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a C++ test generator that accepts command line arguments (argc, argv) and prints input data to stdout.\n"
                "Output ONLY valid C++ code, without markdown code fences."
            )

        def on_success(res_text):
            path, err = create_generator(name)
            target = generator_path(name) if not err else path
            if not target or not os.path.exists(os.path.dirname(target)):
                os.makedirs(GEN_DIR, exist_ok=True)
                target = f"{GEN_DIR}{name}.cpp"
            with open(target, "w", encoding="utf-8") as f:
                f.write(res_text)
            self.input_area.config(text=f"Generated {name} via AI.")
            self.refresh_generators()

        open_ai_dialog(
            self.frame,
            "AI Generator",
            f"Enter prompt for generator '{name}' (C++):",
            wrapper,
            on_success
        )