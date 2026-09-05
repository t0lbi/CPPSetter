import os
import shutil
import tkinter as tk
from tkinter import ttk
from src.core import *

class SubtaskTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
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
        self.main_frame = tk.Frame(self.frame, bg="#333333", width=800)
        self.debug_frame = tk.Frame(self.frame, bg="#333333")
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(side="left", fill="both")
        self.debug_frame.pack(side="right", fill="both", expand=True)


        tk.Label(self.main_frame, text="Name:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        self.subtask_name = tk.Text(self.main_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.subtask_name.pack(padx=5, pady=5, anchor="w")
        tk.Button(self.main_frame, text="Create New Subtask", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.create_subtask_btn).pack(anchor="w", padx=5)


        subtasks=[]
        self.subtasks_combo = ttk.Combobox(self.main_frame, values=subtasks, state="readonly")
        self.subtasks_combo.pack(pady=10, padx=5, anchor="w")
        self.subtasks_combo.bind("<<ComboboxSelected>>", self.on_subtask_select)

        tk.Button(self.main_frame, text="Delete Subtask", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.delete_subtask_btn).pack(anchor="w", padx=5)
        tk.Label(self.main_frame, text="Generator:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)

        generators=[]
        self.generators_combo = ttk.Combobox(self.main_frame, values=generators, state="readonly")
        self.generators_combo.pack(pady=10, padx=5, anchor="w")
        self.generators_combo.bind("<<ComboboxSelected>>", self.on_gen_select)

        tk.Label(self.main_frame, text="Arguments:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        self.gen_args = tk.Text(self.main_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.gen_args.pack(padx=5, pady=5, anchor="w")
        
        gen_runner_frame = tk.Frame(self.main_frame, bg="#333333")
        gen_runner_frame.pack(fill="x", pady=5)
        tk.Button(gen_runner_frame, text="Run", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.run_subtask_gen).pack(side="left", padx=5)
        tk.Button(gen_runner_frame, text="View Input", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.view_subtask_gen_output).pack(side="left", padx=5)
        tk.Button(self.main_frame, text="Add Generator", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.add_gen_to_subtask).pack(anchor="w", padx=5)

        columns = (
            "name",
            "args",
        )
        headings = (
            "Generator Name",
            "Arguments",
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
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        tk.Button(self.main_frame, text="Delete Generator", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.delete_gen_from_subtask).pack(side="left", padx=5)
        input_area = tk.Label(self.debug_frame,font=("Arial", 11), bg="#111111",fg="#ffffff",text="Errors will be shown here.", anchor="nw", justify="left")
        input_area.pack(padx=20, pady=20, fill="both", expand=True)
        self.input_area = input_area

    def create_subtask_btn(self):
        name = self.subtask_name.get("1.0", "end")[:-1].strip()
        if not name:
            return
        res = create_subtask(name)
        if res == 1:
            self.input_area.config(text=f"Created {name}")
            self.refresh_subtasks()
            self.subtasks_combo.set(name)
            self.on_subtask_select()
        else:
            self.input_area.config(text="Subtask creation failed.")

    def on_subtask_select(self, event=None):
        subtask = self.subtasks_combo.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not subtask:
            return
        meta = read_subtask_metadata(subtask)
        first_gen = None
        first_args = None
        for pack in meta.get("data", []):
            gen_name = pack.get("generator", "")
            for flag in pack.get("tests", []):
                if first_gen is None:
                    first_gen = gen_name
                    first_args = flag
                self.tree.insert("", tk.END, values=(gen_name, flag))
        if first_gen:
            self.generators_combo.set(first_gen)
        if first_args is not None:
            self.gen_args.delete("1.0", tk.END)
            self.gen_args.insert("1.0", str(first_args))

    def on_tree_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        item_data = self.tree.item(selected)
        values = item_data.get("values", [])
        if len(values) >= 2:
            self.generators_combo.set(str(values[0]))
            self.gen_args.delete("1.0", tk.END)
            self.gen_args.insert("1.0", str(values[1]))

    def delete_subtask_btn(self):
        subtask = self.subtasks_combo.get()
        if not subtask:
            return
        err = remove_subtask(subtask)
        if err:
            self.input_area.config(text=err)
        else:
            self.input_area.config(text=f"Deleted {subtask}")
            subtasks = list_subtasks()
            self.subtasks_combo.config(values=subtasks)
            if subtasks:
                self.subtasks_combo.set(subtasks[0])
                self.on_subtask_select()
            else:
                self.subtasks_combo.set("")
                for item in self.tree.get_children():
                    self.tree.delete(item)

    def on_gen_select(self, event=None):
        pass

    def run_subtask_gen(self):
        gen = self.generators_combo.get()
        if not gen:
            self.input_area.config(text="No generator selected.")
            return
        args = self.gen_args.get("1.0", "end")[:-1].strip()
        os.makedirs("temp", exist_ok=True)
        exe_path = f"temp/gen_{gen}"
        if os.path.isdir(exe_path):
            shutil.rmtree(exe_path)
        if compile_code(generator_path(gen), "none", "", exe_path) != 1:
            err = get_last_compile_error()
            self.input_area.config(text=err if err else "Compilation error (CE).")
            return
        out_path = "temp/subtask_gen.out"
        if run_gen(exe_path, args, out_path) != 1:
            self.input_area.config(text="Runtime error (RE).")
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

    def view_subtask_gen_output(self):
        out_path = "temp/subtask_gen.out"
        if os.path.isfile(out_path):
            open_in_gnome_text_editor(out_path)
        else:
            self.input_area.config(text="Output file not found.")

    def add_gen_to_subtask(self):
        subtask = self.subtasks_combo.get()
        gen = self.generators_combo.get()
        if not subtask or not gen:
            self.input_area.config(text="Select subtask and generator.")
            return
        args = self.gen_args.get("1.0", "end")[:-1].strip()
        meta = read_subtask_metadata(subtask)
        data = meta.get("data", [])
        found = False
        for pack in data:
            if pack.get("generator") == gen:
                pack.get("tests", []).append(args)
                found = True
                break
        if not found:
            data.append({"generator": gen, "tests": [args]})
        save_subtask_metadata(subtask, meta.get("constraints", ""), data)
        self.tree.insert("", tk.END, values=(gen, args))
        self.input_area.config(text=f"Added {gen} to {subtask}")

    def delete_gen_from_subtask(self):
        subtask = self.subtasks_combo.get()
        selected = self.tree.selection()
        if not subtask or not selected:
            return
        item_data = self.tree.item(selected[0])
        gen = str(item_data["values"][0])
        args = str(item_data["values"][1]) if len(item_data["values"]) > 1 else ""
        meta = read_subtask_metadata(subtask)
        data = meta.get("data", [])
        nw = []
        removed = False
        for pack in data:
            if pack.get("generator") == gen and not removed:
                tests = list(pack.get("tests", []))
                if args in tests:
                    tests.remove(args)
                    removed = True
                if tests:
                    pack["tests"] = tests
                    nw.append(pack)
            else:
                nw.append(pack)
        if not removed:
            nw = [p for p in data if p.get("generator") != gen]
        save_subtask_metadata(subtask, meta.get("constraints", ""), nw)
        self.input_area.config(text=f"Removed {gen} from {subtask}")
        self.on_subtask_select()

    def refresh_subtasks(self):
        self.subtasks_combo.config(values=list_subtasks())

    def update_buttons(self, *args):
        pass

    def update_ui(self):
        subtasks = list_subtasks()
        self.subtasks_combo.config(values=subtasks)
        generators = list_generators()
        self.generators_combo.config(values=generators)
        if subtasks:
            current = self.subtasks_combo.get()
            if not current or current not in subtasks:
                self.subtasks_combo.set(subtasks[0])
            self.on_subtask_select()
        else:
            self.subtasks_combo.set("")
            for item in self.tree.get_children():
                self.tree.delete(item)