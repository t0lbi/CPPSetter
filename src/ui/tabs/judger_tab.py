import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, filedialog
from src.core import *
from src.ui.llm_api_tab import open_ai_dialog

class JudgerTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
        self.button_frame = tk.Frame(self.frame, bg="#333333")
        self.list_frame = tk.Frame(self.frame, bg="#333333")
        self.button_frame.pack(side="left", fill="y")
        self.list_frame.pack(side="right", fill="both", expand=True)


        tk.Button(self.button_frame, text="Create Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.create_submission).pack(padx=10, pady=5)
        self.submission_text = tk.Text(self.button_frame, height=1, width=16, bg="#111111", fg="#ffffff", font=("TkDefaultFont",13))
        self.submission_text.pack(fill="x", padx=5, pady=5)
        tk.Button(self.button_frame, text="Rename Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.rename_submission).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Delete Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.delete_submission).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Edit Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.edit_submission).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Load Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.load_submission).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="AI", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.ask_ai_submission).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Judge Selected", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.judge_selected).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Judge All", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.judge_all).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="View Details", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.view_details).pack(padx=10, pady=5)
        
        self.error_area = tk.Label(self.button_frame, font=("Arial", 11), bg="#111111", fg="#ff0000", text="Errors will be shown here.", anchor="nw", wraplength=160)
        self.error_area.pack(padx=10, pady=10, fill="both", expand=True)

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
            "id",
            "name",
            "pass_cnt",
            "total",
            "time",
            "mem",
            "status",
        )
        headings = (
            "#", 
            "Name",
            "Pass #",
            "Total",
            "Time (ms)",
            "Memory (KB)",
            "Status"
        )
        tree = ttk.Treeview(
            self.list_frame,
            columns=columns,
            show="headings",
            height=25
        )
        for i in range(len(columns)):
            tree.heading(columns[i], text=headings[i])
            tree.column(columns[i], width=len(headings[i])*15+5, anchor="center", stretch=False)
        tree.pack(pady=20, padx=20, fill="both", expand=True)
        self.tree = tree
        self.tree.bind("<<TreeviewSelect>>", self.on_submission_select)

    def get_submissions_dirs(self):
        dirs = []
        if hasattr(self.main, "current_problem_name") and self.main.current_problem_name:
            dirs.append(f"temp/{self.main.current_problem_name}/submissions")
        dirs.append(f"{PROBLEM_DIR}submissions")
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        if len(dirs) > 1:
            for f in os.listdir(dirs[1]):
                dest = os.path.join(dirs[0], f)
                if not os.path.exists(dest):
                    src = os.path.join(dirs[1], f)
                    if os.path.isfile(src):
                        shutil.copy2(src, dest)
            for f in os.listdir(dirs[0]):
                dest = os.path.join(dirs[1], f)
                if not os.path.exists(dest):
                    src = os.path.join(dirs[0], f)
                    if os.path.isfile(src):
                        shutil.copy2(src, dest)
        return dirs

    def format_submission_json(self, details):
        if not details.get("tests"):
            return json.dumps(details, indent=2) + "\n"
        tests = details["tests"]
        base = {k: v for k, v in details.items() if k != "tests"}
        tests_str = ",\n    ".join(json.dumps(t) for t in tests)
        if not base:
            return "{\n  \"tests\": [\n    " + tests_str + "\n  ]\n}\n"
        base_str = json.dumps(base, indent=2)
        return base_str[:-2] + ",\n  \"tests\": [\n    " + tests_str + "\n  ]\n}\n"

    def create_submission(self):
        dirs = self.get_submissions_dirs()
        primary_dir = dirs[0]
        x = 1
        while os.path.exists(f"{primary_dir}/New Submission({x}).cpp"):
            x += 1
        sub_name = f"New Submission({x})"
        stub = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n\treturn 0;\n}\n"
        default_meta = {
            "status": "-",
            "pass_cnt": 0,
            "total": 0,
            "time": "-",
            "runtime": "-",
            "mem": "-",
            "memory": "-",
            "tests": []
        }
        formatted_json = self.format_submission_json(default_meta)
        for d in dirs:
            cpp_path = f"{d}/{sub_name}.cpp"
            json_path = f"{d}/{sub_name}.json"
            with open(cpp_path, "w", encoding="utf-8") as f:
                f.write(stub)
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(formatted_json)
        self.submission_text.delete("1.0", tk.END)
        self.submission_text.insert("1.0", sub_name)
        self.update_ui()
        self.error_area.config(text=f"Created {sub_name}.cpp")
        for item in self.tree.get_children():
            values = self.tree.item(item).get("values", [])
            if len(values) >= 2 and str(values[1]) == sub_name:
                self.tree.selection_set(item)
                self.tree.focus(item)
                break

    def on_submission_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        item_data = self.tree.item(selected[0])
        values = item_data.get("values", [])
        if len(values) >= 2:
            sub_name = str(values[1])
            self.submission_text.delete("1.0", tk.END)
            self.submission_text.insert("1.0", sub_name)

    def rename_submission(self):
        selected = self.tree.selection()
        if not selected:
            self.error_area.config(text="No submission selected.")
            return
        item_data = self.tree.item(selected[0])
        old_name = str(item_data.get("values", [])[1])
        if old_name.endswith(".cpp"):
            old_name = old_name[:-4]
        new_name = self.submission_text.get("1.0", "end")[:-1].strip()
        if not new_name:
            self.error_area.config(text="Submission name cannot be empty.")
            return
        if new_name.endswith(".cpp"):
            new_name = new_name[:-4]
        if old_name == new_name:
            return
        dirs = self.get_submissions_dirs()
        for d in dirs:
            old_cpp = f"{d}/{old_name}.cpp"
            new_cpp = f"{d}/{new_name}.cpp"
            old_json = f"{d}/{old_name}.json"
            new_json = f"{d}/{new_name}.json"
            if os.path.exists(new_cpp) and old_cpp != new_cpp:
                self.error_area.config(text=f"Submission {new_name}.cpp already exists.")
                return
            if os.path.isfile(old_cpp):
                os.rename(old_cpp, new_cpp)
            if os.path.isfile(old_json):
                os.rename(old_json, new_json)
        self.error_area.config(text=f"Renamed to {new_name}.cpp")
        self.update_ui()
        for item in self.tree.get_children():
            values = self.tree.item(item).get("values", [])
            if len(values) >= 2 and str(values[1]) == new_name:
                self.tree.selection_set(item)
                self.tree.focus(item)
                break

    def delete_submission(self):
        selected = self.tree.selection()
        if not selected:
            self.error_area.config(text="No submission selected.")
            return
        item_data = self.tree.item(selected[0])
        sub_name = str(item_data.get("values", [])[1])
        if sub_name.endswith(".cpp"):
            sub_name = sub_name[:-4]
        dirs = self.get_submissions_dirs()
        for d in dirs:
            cpp_path = f"{d}/{sub_name}.cpp"
            json_path = f"{d}/{sub_name}.json"
            if os.path.isfile(cpp_path):
                os.remove(cpp_path)
            if os.path.isfile(json_path):
                os.remove(json_path)
        self.submission_text.delete("1.0", tk.END)
        self.error_area.config(text=f"Deleted {sub_name}")
        self.update_ui()

    def edit_submission(self):
        selected = self.tree.selection()
        if not selected:
            self.error_area.config(text="No submission selected.")
            return
        item_data = self.tree.item(selected[0])
        sub_name = str(item_data.get("values", [])[1])
        if sub_name.endswith(".cpp"):
            sub_name = sub_name[:-4]
        dirs = self.get_submissions_dirs()
        cpp_path = f"{dirs[0]}/{sub_name}.cpp"
        if os.path.isfile(cpp_path):
            open_in_gnome_text_editor(cpp_path)
        else:
            self.error_area.config(text="Submission file not found.")

    def load_submission(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        selected = self.tree.selection()
        if selected:
            item_data = self.tree.item(selected[0])
            sub_name = str(item_data.get("values", [])[1])
            if sub_name.endswith(".cpp"):
                sub_name = sub_name[:-4]
        else:
            text_name = self.submission_text.get("1.0", "end")[:-1].strip()
            if text_name:
                sub_name = text_name[:-4] if text_name.endswith(".cpp") else text_name
            else:
                base = os.path.basename(path)
                sub_name = base[:-4] if base.endswith(".cpp") else base
        dirs = self.get_submissions_dirs()
        for d in dirs:
            dest_cpp = f"{d}/{sub_name}.cpp"
            dest_json = f"{d}/{sub_name}.json"
            shutil.copy2(path, dest_cpp)
            if not os.path.isfile(dest_json):
                default_meta = {
                    "status": "-",
                    "pass_cnt": 0,
                    "total": 0,
                    "time": "-",
                    "runtime": "-",
                    "mem": "-",
                    "memory": "-",
                    "tests": []
                }
                with open(dest_json, "w", encoding="utf-8") as f:
                    f.write(self.format_submission_json(default_meta))
        self.error_area.config(text=f"Imported {os.path.basename(path)} as {sub_name}.cpp")
        self.update_ui()

    def view_details(self):
        selected = self.tree.selection()
        if not selected:
            self.error_area.config(text="No submission selected.")
            return
        item_data = self.tree.item(selected[0])
        sub_name = str(item_data.get("values", [])[1])
        if sub_name.endswith(".cpp"):
            sub_name = sub_name[:-4]
        dirs = self.get_submissions_dirs()
        json_path = f"{dirs[0]}/{sub_name}.json"
        if not os.path.isfile(json_path):
            default_meta = {
                "status": "-",
                "pass_cnt": 0,
                "total": 0,
                "time": "-",
                "runtime": "-",
                "mem": "-",
                "memory": "-",
                "tests": []
            }
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(self.format_submission_json(default_meta))
        open_in_gnome_text_editor(json_path)

    def judge_submission(self, sub_name):
        dirs = self.get_submissions_dirs()
        primary_dir = dirs[0]
        cpp_path = f"{primary_dir}/{sub_name}.cpp"
        if not os.path.isfile(cpp_path):
            self.error_area.config(text=f"File not found: {sub_name}.cpp")
            return False
        meta = read_metadata()
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return False
        os.makedirs("temp", exist_ok=True)
        exe_path = f"temp/sub_{sub_name}"
        if compile_code(cpp_path, grader_cpp, "", exe_path) != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else f"CE: {sub_name}.cpp")
            details = {
                "status": "CE",
                "pass_cnt": 0,
                "total": 0,
                "time": "-",
                "runtime": "-",
                "mem": "-",
                "memory": "-",
                "tests": [],
                "error": err if err else "Compilation error (CE)"
            }
            formatted_json = self.format_submission_json(details)
            for d in dirs:
                with open(f"{d}/{sub_name}.json", "w", encoding="utf-8") as f:
                    f.write(formatted_json)
            return False
        checker_exe, checker_err = compile_checker_executable(meta)
        if checker_err:
            self.error_area.config(text=checker_err)
            return False
        if checker_exe is None:
            checker_exe = "none"
        time_limit = float(meta.get("time_limit", 2.0))
        time_limit_ms = int(time_limit * 1000)
        memory_limit = float(meta.get("memory_limit", 256.0))
        memory_limit_kb = int(memory_limit * 1024)
        subtasks = list_subtasks()
        tests_record = []
        pass_cnt = 0
        total_tests = 0
        max_time = 0
        max_mem = 0
        overall_status = "AC"
        for subtask in subtasks:
            in_dir = f"{PROBLEM_DIR}{subtask}/input"
            out_dir = f"{PROBLEM_DIR}{subtask}/output"
            if not (os.path.isdir(in_dir) and [f for f in os.listdir(in_dir) if f.endswith('.in')]):
                if hasattr(self.main, "current_problem_name") and self.main.current_problem_name:
                    curr_in = f"temp/{self.main.current_problem_name}/{subtask}/input"
                    curr_out = f"temp/{self.main.current_problem_name}/{subtask}/output"
                    if os.path.isdir(curr_in) and [f for f in os.listdir(curr_in) if f.endswith('.in')]:
                        in_dir = curr_in
                        out_dir = curr_out
            if not (os.path.isdir(in_dir) and [f for f in os.listdir(in_dir) if f.endswith('.in')]):
                io_in = f"temp/io/{subtask}/input"
                io_out = f"temp/io/{subtask}/output"
                if os.path.isdir(io_in) and [f for f in os.listdir(io_in) if f.endswith('.in')]:
                    in_dir = io_in
                    out_dir = io_out
            if not os.path.isdir(in_dir):
                continue
            in_files = sorted([f for f in os.listdir(in_dir) if f.endswith(".in")], key=lambda x: int(x[:-3]) if x[:-3].isdigit() else x)
            for f in in_files:
                test_num = f[:-3]
                in_path = f"{in_dir}/{f}"
                out_path = f"{out_dir}/{test_num}.out"
                sub_out = f"temp/sub_run_{sub_name}_{subtask}_{test_num}.out"
                run_res = run_exec(exe_path, in_path, sub_out)
                total_tests += 1
                run_ok = run_res[0]
                run_time = run_res[1]
                run_mem = run_res[2]
                if run_time > max_time:
                    max_time = run_time
                if run_mem > max_mem:
                    max_mem = run_mem
                if run_mem > memory_limit_kb:
                    verdict = "MLE"
                elif run_time > time_limit_ms:
                    verdict = "TLE"
                elif run_ok != 1:
                    verdict = "RE"
                else:
                    if not os.path.isfile(out_path):
                        verdict = "WA"
                    else:
                        s = score(in_path, sub_out, out_path, checker_exe)
                        if s == 1.0:
                            verdict = "AC"
                        else:
                            verdict = "WA"
                if verdict == "AC":
                    pass_cnt += 1
                else:
                    if overall_status == "AC":
                        overall_status = verdict
                tests_record.append([
                    subtask,
                    int(test_num) if test_num.isdigit() else test_num,
                    verdict,
                    run_time,
                    run_mem
                ])
                if os.path.isfile(sub_out):
                    os.remove(sub_out)
        if total_tests == 0:
            overall_status = "-"
        details = {
            "status": overall_status,
            "pass_cnt": pass_cnt,
            "total": total_tests,
            "time": max_time if total_tests > 0 else "-",
            "runtime": max_time if total_tests > 0 else "-",
            "mem": max_mem if total_tests > 0 else "-",
            "memory": max_mem if total_tests > 0 else "-",
            "tests": tests_record
        }
        formatted_json = self.format_submission_json(details)
        for d in dirs:
            with open(f"{d}/{sub_name}.json", "w", encoding="utf-8") as f:
                f.write(formatted_json)
        return True

    def judge_selected(self):
        selected = self.tree.selection()
        if not selected:
            text_name = self.submission_text.get("1.0", "end")[:-1].strip()
            if text_name:
                sub_name = text_name[:-4] if text_name.endswith(".cpp") else text_name
            else:
                self.error_area.config(text="No submission selected.")
                return
        else:
            item_data = self.tree.item(selected[0])
            sub_name = str(item_data.get("values", [])[1])
            if sub_name.endswith(".cpp"):
                sub_name = sub_name[:-4]
        res = self.judge_submission(sub_name)
        self.update_ui()
        if res:
            dirs = self.get_submissions_dirs()
            json_path = f"{dirs[0]}/{sub_name}.json"
            if os.path.isfile(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.error_area.config(text=f"{sub_name}: {data.get('status')} ({data.get('pass_cnt')}/{data.get('total')})")

    def judge_all(self):
        dirs = self.get_submissions_dirs()
        primary_dir = dirs[0]
        cpp_files = sorted([f for f in os.listdir(primary_dir) if f.endswith(".cpp")])
        if not cpp_files:
            self.error_area.config(text="No submissions found.")
            return
        for f in cpp_files:
            sub_name = f[:-4]
            self.judge_submission(sub_name)
        self.update_ui()
        self.error_area.config(text="Judged all submissions.")

    def update_buttons(self, *args):
        pass

    def update_ui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        dirs = self.get_submissions_dirs()
        primary_dir = dirs[0]
        cpp_files = sorted([f for f in os.listdir(primary_dir) if f.endswith(".cpp")])
        for idx in range(len(cpp_files)):
            sub_name = cpp_files[idx][:-4]
            json_path = f"{primary_dir}/{sub_name}.json"
            pass_cnt = "-"
            total = "-"
            time_val = "-"
            mem_val = "-"
            status = "-"
            if os.path.isfile(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pass_cnt = str(data.get("pass_cnt", "-"))
                    total = str(data.get("total", "-"))
                    time_val = str(data.get("time", "-"))
                    mem_val = str(data.get("mem", "-"))
                    status = str(data.get("status", "-"))
                except Exception:
                    pass
            self.tree.insert("", tk.END, values=(idx + 1, sub_name, pass_cnt, total, time_val, mem_val, status))

    def ask_ai_submission(self):
        selected = self.tree.selection()
        sub_name = ""
        if selected:
            item_data = self.tree.item(selected[0])
            sub_name = str(item_data.get("values", [])[1])
            if sub_name.endswith(".cpp"):
                sub_name = sub_name[:-4]
        else:
            text_name = self.submission_text.get("1.0", "end")[:-1].strip()
            if text_name:
                sub_name = text_name[:-4] if text_name.endswith(".cpp") else text_name

        dirs = self.get_submissions_dirs()
        primary_dir = dirs[0]
        if not sub_name:
            x = 1
            while os.path.exists(f"{primary_dir}/New Submission({x}).cpp"):
                x += 1
            sub_name = f"New Submission({x})"

        target_name = sub_name

        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input Format: {meta.get('input', '')}\n"
                f"Output Format: {meta.get('output', '')}\n"
                f"Constraints: {meta.get('constraints', '')}\n"
            )
            return (
                "You are an assistant for competitive programming problem setters.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a C++ submission solution for this problem.\n"
                "Output ONLY valid C++ code, without markdown code fences."
            )

        def on_success(res_text):
            for d in dirs:
                cpp_path = f"{d}/{target_name}.cpp"
                json_path = f"{d}/{target_name}.json"
                with open(cpp_path, "w", encoding="utf-8") as f:
                    f.write(res_text)
                if not os.path.isfile(json_path):
                    default_meta = {
                        "status": "-",
                        "pass_cnt": 0,
                        "total": 0,
                        "time": "-",
                        "runtime": "-",
                        "mem": "-",
                        "memory": "-",
                        "tests": []
                    }
                    with open(json_path, "w", encoding="utf-8") as f:
                        f.write(self.format_submission_json(default_meta))
            self.submission_text.delete("1.0", tk.END)
            self.submission_text.insert("1.0", target_name)
            self.update_ui()
            self.error_area.config(text=f"Generated {target_name}.cpp via AI.")

        open_ai_dialog(
            self.frame,
            "AI Submission Generator",
            f"Enter prompt for submission '{target_name}' (C++):",
            wrapper,
            on_success
        )