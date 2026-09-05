import os
import shutil
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog
import src.core.manager as mgr

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
        ).pack(pady=(150, 0))
        platforms = ["Codeforces", "CMS", "Algoleague"]
        self.platforms_combo = ttk.Combobox(self.frame, values=platforms, state="readonly", font=("Arial", 25))
        self.platforms_combo.pack(pady=75)
        self.platforms_combo.current(0)

        self.export_button = tk.Button(
            self.frame,
            text="Export to...",
            font=("Arial", 25),
            width=15,
            height=3,
            bg="#3c3f41",
            fg="#ffffff",
            command=self.export_package
        )
        self.export_button.pack()

        self.status_label = tk.Label(
            self.frame,
            text="",
            bg="#333333",
            fg="#00ff00",
            font=("Arial", 16),
            wraplength=600
        )
        self.status_label.pack(pady=20)

    def export_package(self):
        prob_name = getattr(self.main, "current_problem_name", None)
        if not prob_name:
            try:
                meta = mgr.read_metadata()
                prob_name = meta.get("title", "").strip()
            except Exception:
                prob_name = ""
        if not prob_name:
            self.status_label.config(text="No problem loaded.", fg="#ff0000")
            return

        dest_dir = filedialog.askdirectory(title="Select Destination Folder")
        if not dest_dir:
            return

        platform = self.platforms_combo.get().strip()
        if not platform:
            self.status_label.config(text="Please select a target platform.", fg="#ff0000")
            return

        export_folder_name = f"{prob_name}_export"
        export_path = os.path.join(dest_dir, export_folder_name)
        os.makedirs(export_path, exist_ok=True)

        meta = mgr.read_metadata()
        checker_src = None
        for p in [
            f"{mgr.PROBLEM_DIR}checker.cpp",
            f"temp/{prob_name}/checker.cpp",
            f"problems/{prob_name}/checker.cpp"
        ]:
            if os.path.isfile(p):
                checker_src = p
                break
        has_checker = False
        if checker_src:
            if meta.get("checker"):
                has_checker = True
            else:
                try:
                    with open(checker_src, "r", encoding="utf-8") as f:
                        c = f.read().strip()
                    if c and c != mgr._CHECKER_STUB.strip():
                        has_checker = True
                except Exception:
                    pass
        if has_checker and checker_src:
            shutil.copy2(checker_src, os.path.join(export_path, "checker.cpp"))

        grader_src = None
        for p in [
            f"{mgr.PROBLEM_DIR}grader.cpp",
            f"temp/{prob_name}/grader.cpp",
            f"problems/{prob_name}/grader.cpp"
        ]:
            if os.path.isfile(p):
                grader_src = p
                break
        has_grader = False
        if grader_src:
            if meta.get("grader"):
                has_grader = True
            else:
                try:
                    with open(grader_src, "r", encoding="utf-8") as f:
                        c = f.read().strip()
                    if c and c != mgr._GRADER_STUB.strip():
                        has_grader = True
                except Exception:
                    pass
        if has_grader and grader_src:
            shutil.copy2(grader_src, os.path.join(export_path, "grader.cpp"))

        sol_src = None
        for p in [
            mgr.FULL_SOLUTION_PATH,
            f"{mgr.PROBLEM_DIR}solutions/full.cpp",
            f"temp/{prob_name}/solutions/full.cpp",
            f"problems/{prob_name}/solutions/full.cpp",
            f"{mgr.PROBLEM_DIR}solutions/solution.cpp",
            f"{mgr.PROBLEM_DIR}solution.cpp",
            f"temp/{prob_name}/solution.cpp",
            f"problems/{prob_name}/solution.cpp"
        ]:
            if os.path.isfile(p):
                sol_src = p
                break
        if sol_src:
            shutil.copy2(sol_src, os.path.join(export_path, "solution.cpp"))

        export_subs_dir = os.path.join(export_path, "submissions")
        os.makedirs(export_subs_dir, exist_ok=True)
        sub_dirs = [
            f"temp/{prob_name}/submissions",
            f"{mgr.PROBLEM_DIR}submissions",
            f"problems/{prob_name}/submissions"
        ]
        copied_subs = set()
        for s_dir in sub_dirs:
            if os.path.isdir(s_dir):
                for fname in sorted(os.listdir(s_dir)):
                    s_file = os.path.join(s_dir, fname)
                    if os.path.isfile(s_file) and not fname.endswith(".json") and fname not in copied_subs:
                        shutil.copy2(s_file, os.path.join(export_subs_dir, fname))
                        copied_subs.add(fname)

        subtasks = mgr.list_subtasks()
        if not subtasks:
            subtasks = meta.get("subtasks", [])

        all_tests = []
        for subtask in subtasks:
            in_candidates = [
                f"{mgr.PROBLEM_DIR}{subtask}/input",
                f"temp/{prob_name}/{subtask}/input",
                f"temp/{subtask}/input",
                f"temp/io/{subtask}/input",
                f"problems/{prob_name}/{subtask}/input"
            ]
            out_candidates = [
                f"{mgr.PROBLEM_DIR}{subtask}/output",
                f"temp/{prob_name}/{subtask}/output",
                f"temp/{subtask}/output",
                f"temp/io/{subtask}/output",
                f"problems/{prob_name}/{subtask}/output"
            ]
            in_dir = None
            for p in in_candidates:
                if os.path.isdir(p) and any(f.endswith(".in") for f in os.listdir(p)):
                    in_dir = p
                    break
            out_dir = None
            for p in out_candidates:
                if os.path.isdir(p) and any(f.endswith(".out") for f in os.listdir(p)):
                    out_dir = p
                    break
            if not in_dir:
                continue
            in_files = sorted(
                [f for f in os.listdir(in_dir) if f.endswith(".in")],
                key=lambda x: int(x[:-3]) if x[:-3].isdigit() else x
            )
            subtask_test_list = []
            for f in in_files:
                test_num = f[:-3]
                in_fpath = os.path.join(in_dir, f)
                out_fpath = None
                if out_dir and os.path.isfile(os.path.join(out_dir, f"{test_num}.out")):
                    out_fpath = os.path.join(out_dir, f"{test_num}.out")
                else:
                    for oc in out_candidates:
                        cand = os.path.join(oc, f"{test_num}.out")
                        if os.path.isfile(cand):
                            out_fpath = cand
                            break
                subtask_test_list.append({
                    "test_num": test_num,
                    "in": in_fpath,
                    "out": out_fpath
                })
            all_tests.append((subtask, subtask_test_list))

        zip_path = os.path.join(export_path, "tests.zip")
        plat_lower = platform.lower()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            if "algo" in plat_lower:
                global_idx = 1
                for subtask, tests in all_tests:
                    for t in tests:
                        fname = f"{global_idx:02d}.txt"
                        zipf.write(t["in"], f"input/{fname}")
                        if t["out"] and os.path.isfile(t["out"]):
                            zipf.write(t["out"], f"output/{fname}")
                        global_idx += 1
            elif "codeforces" in plat_lower:
                for subtask, tests in all_tests:
                    for idx, t in enumerate(tests, 1):
                        test_idx = int(t["test_num"]) if t["test_num"].isdigit() else idx
                        fname = f"{subtask}_{test_idx:02d}.txt"
                        zipf.write(t["in"], fname)
            elif "cms" in plat_lower:
                for subtask, tests in all_tests:
                    for idx, t in enumerate(tests, 1):
                        test_idx = int(t["test_num"]) if t["test_num"].isdigit() else idx
                        in_name = f"{subtask}_{test_idx:02d}.in"
                        zipf.write(t["in"], in_name)
                        if t["out"] and os.path.isfile(t["out"]):
                            out_name = f"{subtask}_{test_idx:02d}.out"
                            zipf.write(t["out"], out_name)

        self.status_label.config(text=f"Exported successfully to {export_folder_name}", fg="#00ff00")