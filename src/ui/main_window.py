import os
import shutil
import tkinter as tk
from tkinter import messagebox
from src.core.manager import *
from src.ui.tabs import *

class MainWindow:
	def __init__(self, root: tk.Tk):
		self.root = root
		self.current_problem_name = None
		self.root.title("CPP Setter")
		self.root.geometry("1300x840")
		self.root.config(bg="#2b2b2b")
		self.build_layout()
		self.init_views()
		self.root.protocol("WM_DELETE_WINDOW", self.on_close)
		self.show_view("Entry")

	def build_layout(self):
		self.nav_frame = tk.Frame(self.root, width=150, bg="#1e1e1e")
		self.nav_frame.pack(side="left", fill="y")
		tk.Label(
			self.nav_frame,
			text="Menu",
			font=("Arial", 12, "bold"),
			bg="#1e1e1e",
			fg="#ffffff",
		).pack(pady=10)
		self.nav_buttons_frame = tk.Frame(self.nav_frame, bg="#1e1e1e")
		self.nav_buttons_frame.pack()
		self.problem_name_label = tk.Label(
			self.nav_frame,
			text="No problem",
			font=("Arial", 9),
			bg="#1e1e1e",
			fg="#888888",
			wraplength=130,
			justify="center",
		)
		self.problem_name_label.pack(side="bottom",pady=8)
		self.save_btn = tk.Button(
			self.nav_frame,
			text="Save",
			width=15,
			bg="#3c3f41",
			fg="#ffffff",
			state="disabled",
			command=self.save_current_problem,
		)
		self.save_btn.pack(side="bottom")

		self.deneme_btn = tk.Button(
			self.nav_frame,
			text="UU",
			width=15,
			bg="#3c3f41",
			fg="#ffffff",
			command=lambda: self.set_current_problem("probname"),
		)
		self.deneme_btn.pack(side="bottom")



		self.container = tk.Frame(self.root)
		self.container.pack(side="right", fill="both", expand=True)
		self.container.grid_rowconfigure(0, weight=1)
		self.container.grid_columnconfigure(0, weight=1)

	def init_views(self):
		self.views = {}
		self.nav_buttons = {}
		self.views["Entry"] = EntryTab(self.container, self)
		self.views["Problem Info"] = ProblemTab(self.container, self)
		self.views["Brute Force"] = BruteTab(self.container, self)
		self.views["Solution"] = SolutionTab(self.container, self)
		self.views["Generators"] = GeneratorsTab(self.container, self)
		self.views["Subtasks"] = SubtaskTab(self.container, self)
		self.views["I/O"] = IOTab(self.container, self)
		self.views["Judger"] = JudgerTab(self.container, self)
		self.views["Exporter"] = ExporterTab(self.container, self)
		for name, view_obj in self.views.items():
			view_obj.frame.grid(row=0, column=0, sticky="nsew")
			btn = tk.Button(
				self.nav_buttons_frame,
				text=name,
				width=15,
				bg="#3c3f41",
				fg="#ffffff",
				command=lambda n=name: self.show_view(n),
			)
			btn.pack(pady=5, padx=10)
			self.nav_buttons[name] = btn
		self.update_nav()

	def can_save(self):
		return os.path.isdir("temp/problem-data") and self.current_problem_name is not None

	def update_nav(self):
		has_problem = self.can_save()
		for name, btn in self.nav_buttons.items():
			if name == "Entry":
				btn.config(state="normal")
			else:
				if has_problem:
					btn.config(state="normal")
				else:
					btn.config(state="disabled")

		if has_problem:
			self.save_btn.config(state="normal")
			self.problem_name_label.config(
				text=self.current_problem_name
			)
		else:
			self.save_btn.config(state="disabled")
			self.problem_name_label.config(text="No problem")

	def save_current_problem(self):
		if not self.can_save():
			messagebox.showwarning("Save", "Nothing to save — open or create a problem first.")
			return False
		if save_problem(self.current_problem_name) != 1:
			return False
		return True

	def on_close(self):
		if self.can_save() and workspace_differs_from_saved(self.current_problem_name):
			choice = messagebox.askyesnocancel(
				"Unsaved changes",
				"Workspace differs from the saved copy. Save before closing?",
			)
			if choice is None:
				return
			if choice:
				if not self.save_current_problem():
					return
		if os.path.exists("temp/"):
			shutil.rmtree("temp/")
		self.root.destroy()

	def show_view(self, view_name):
		if view_name != "Entry" and not self.can_save():
			return
		view_obj = self.views[view_name]
		view_obj.frame.tkraise()
		title = f"CPP Setter - {view_name}"
		if self.current_problem_name:
			title += f" — {self.current_problem_name}"
		self.root.title(title)