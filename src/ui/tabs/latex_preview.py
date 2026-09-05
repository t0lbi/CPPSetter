import os
import re
import glob
import shutil
import subprocess
import tempfile
import json
import tkinter as tk
from src.core import read_metadata

from PIL import Image, ImageTk


def generate_latex():
	data = read_metadata()
	title = data.get("title", "")
	time_limit = data.get("time_limit", 1.0)
	memory_limit = data.get("memory_limit", 256.0)
	description = data.get("description", "")
	inp = data.get("input", "")
	out = data.get("output", "")
	constraints = data.get("constraints", "")
	solution = data.get("solution", "")
	body = f"""
		\\begin{{center}}
		\\textbf{{\\LARGE {title}}} \\\\
		\\vspace{{0.2em}}
		{{\\small Time Limit: {time_limit}s \\quad Memory Limit: {memory_limit}MB}}
		\\end{{center}}
		
		\\textbf{{Description}}\\\\
		{description}

		\\textbf{{Input}}\\\\
		{inp}

		\\textbf{{Output}}\\\\
		{out}

		\\textbf{{Constraints}}\\\\
		${constraints}$

		\\textbf{{Solution}}\\\\
		{solution}
	"""

	return (
		r"\documentclass[11pt]{article}" "\n"
		r"\usepackage[utf8]{inputenc}" "\n"
		r"\usepackage{amsmath,amssymb}" "\n"
		r"\usepackage[margin=14mm]{geometry}" "\n"
		r"\pagestyle{empty}" "\n"
		r"\setlength{\parindent}{0pt}" "\n"
		r"\setlength{\parskip}{0.8em}" "\n"
		r"\begin{document}" "\n"
		f"{body}\n"
		r"\end{document}"
	)


def wrap_latex_body(body: str) -> str:
	stripped = body.strip()
	if stripped.startswith("\\documentclass"):
		return stripped
	return (
		r"\documentclass[11pt]{article}"
		"\n"
		r"\usepackage[utf8]{inputenc}"
		"\n"
		r"\usepackage{amsmath,amssymb}"
		"\n"
		r"\usepackage[margin=14mm]{geometry}"
		"\n"
		r"\setcounter{secnumdepth}{0}"
		"\n"
		r"\pagestyle{empty}"
		"\n"
		r"\setlength{\parindent}{0pt}"
		"\n"
		r"\begin{document}"
		"\n"
		f"{body}\n"
		r"\end{document}"
	)


class LatexTab:
	def __init__(self, parent, main=None):
		self.parent = parent
		self.main = main
		self.frame = tk.Frame(parent, bg="#111111")
		self.frame.pack(fill="both", expand=True)
		self.image_refs = []
		self.page_files = []
		self._last_w = 0
		self._resize_job = None
		self._build_ui()

	def _build_ui(self):
		self.toolbar = tk.Frame(self.frame, bg="#222222")
		self.toolbar.pack(fill="x", side="top", padx=5, pady=5)

		self.refresh_btn = tk.Button(
			self.toolbar,
			text="Refresh PDF",
			bg="#3c3f41",
			fg="#ffffff",
			font=("Arial", 10),
			command=self.render_preview
		)
		self.refresh_btn.pack(side="left", padx=5)

		self.open_btn = tk.Button(
			self.toolbar,
			text="Open PDF",
			bg="#3c3f41",
			fg="#ffffff",
			font=("Arial", 10),
			command=self.open_pdf
		)
		self.open_btn.pack(side="left", padx=5)

		self.status_lbl = tk.Label(
			self.toolbar,
			text="",
			bg="#222222",
			fg="#aaaaaa",
			font=("Arial", 9)
		)
		self.status_lbl.pack(side="left", padx=10)

		self.canvas_frame = tk.Frame(self.frame, bg="#111111")
		self.canvas_frame.pack(fill="both", expand=True)

		self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical")
		self.scrollbar.pack(side="right", fill="y")

		self.canvas = tk.Canvas(
			self.canvas_frame,
			bg="#1e1e1e",
			highlightthickness=0,
			yscrollcommand=self.scrollbar.set
		)
		self.canvas.pack(side="left", fill="both", expand=True)
		self.scrollbar.config(command=self.canvas.yview)

		self.canvas.bind("<Configure>", self.on_canvas_configure)
		self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
		self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))
		self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

	def on_canvas_configure(self, event):
		if abs(event.width - self._last_w) > 30 and self.page_files:
			if self._resize_job is not None:
				self.frame.after_cancel(self._resize_job)
			self._resize_job = self.frame.after(200, self.draw_pages)
		self._last_w = event.width

	def draw_pages(self):
		self.canvas.delete("all")
		self.image_refs.clear()
		cw = self.canvas.winfo_width()
		target_w = max(250, cw - 30) if cw > 50 else 550
		cur_y = 15
		max_w = target_w
		for page_file in self.page_files:
			try:
				img = Image.open(page_file)
				orig_w, orig_h = img.size
				ratio = target_w / orig_w
				target_h = int(orig_h * ratio)
				resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
				photo = ImageTk.PhotoImage(resized)
				self.image_refs.append(photo)
				self.canvas.create_image(15, cur_y, anchor="nw", image=photo)
				cur_y += target_h + 15
			except Exception:
				pass
		self.canvas.config(scrollregion=(0, 0, max_w + 30, cur_y))

	def open_pdf(self):
		pdf_path = "temp/problem.pdf"
		if os.path.isfile(pdf_path):
			try:
				subprocess.Popen(["xdg-open", pdf_path])
			except Exception as e:
				self.status_lbl.config(text=f"Error opening PDF: {e}", fg="#ff5555")
		else:
			self.status_lbl.config(text="PDF not generated yet", fg="#ff5555")

	def render_preview(self):
		os.makedirs("temp", exist_ok=True)
		tex_content = generate_latex()
		tex_path = "temp/problem.tex"
		pdf_path = "temp/problem.pdf"
		with open(tex_path, "w", encoding="utf-8") as f:
			f.write(tex_content)

		for old_img in glob.glob("temp/problem_page-*.png"):
			try:
				os.remove(old_img)
			except Exception:
				pass

		if os.path.isfile(pdf_path):
			try:
				os.remove(pdf_path)
			except Exception:
				pass

		try:
			subprocess.run(
				["pdflatex", "-interaction=nonstopmode", "-output-directory=temp", tex_path],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				timeout=15
			)
		except Exception as e:
			self.status_lbl.config(text=f"pdflatex error: {e}", fg="#ff5555")
			return

		if not os.path.isfile(pdf_path):
			self.canvas.delete("all")
			self.image_refs.clear()
			self.status_lbl.config(text="LaTeX compilation failed", fg="#ff5555")
			self.canvas.create_text(
				20, 20,
				anchor="nw",
				text="LaTeX compilation failed.\nPlease check syntax or characters.",
				fill="#ff5555",
				font=("Arial", 11)
			)
			return

		try:
			subprocess.run(
				["pdftoppm", "-png", "-r", "150", pdf_path, "temp/problem_page"],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				timeout=15
			)
		except Exception as e:
			self.status_lbl.config(text=f"pdftoppm error: {e}", fg="#ff5555")
			return

		page_files = sorted(glob.glob("temp/problem_page-*.png"))
		if not page_files:
			self.status_lbl.config(text="Failed to convert PDF pages", fg="#ff5555")
			return

		self.page_files = page_files
		self.draw_pages()
		self.status_lbl.config(text="PDF preview updated", fg="#55ff55")

	def update_ui(self):
		self.render_preview()


LatexPreview = LatexTab