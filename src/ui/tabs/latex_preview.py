import os
import re
import shutil
import subprocess
import tempfile
import json
from src.core import read_metadata

from PIL import Image


def generate_latex():
	data = read_metadata()
	body = f"""
		\\begin{{center}}
		\\textbf{{\\LARGE {data['title']}}} \\\\
		\\vspace{{0.2em}}
		{{\\small Time Limit: {data['time_limit']}s \\quad Memory Limit: {data['memory_limit']}MB}}
		\\end{{center}}
		
		\\textbf{{Description}}\\\\
		{data['description']}

		\\textbf{{Input}}\\\\
		{data['input']}

		\\textbf{{Output}}\\\\
		{data['output']}

		\\textbf{{Constraints}}\\\\
		${data['constraints']}$

		\\textbf{{Solution}}\\\\
		{data['solution']}
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