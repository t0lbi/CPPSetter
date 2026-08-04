from src import *
import os
import shutil
import subprocess
import json
from dotenv import load_dotenv

if os.path.exists("temp"):
    shutil.rmtree("temp")
os.makedirs("temp", exist_ok=True)
if not os.path.exists("problems"):
	os.makedirs("problems", exist_ok=True)

load_dotenv()
root = tk.Tk()
app = MainWindow(root)
root.mainloop()