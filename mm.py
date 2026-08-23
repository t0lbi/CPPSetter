import tkinter as tk
from tkinter import ttk

def show_row_selected(event):
    # Identify selected row item
    selected_item = tree.selection()
    if selected_item:
        # Extract row dictionary values
        item_data = tree.item(selected_item)
        print(f"Row Data: {item_data['values']}")

root = tk.Tk()
root.title("Treeview Grid Example")
root.geometry("450x250")

# Define column names
columns = ("id", "name", "role")
tree = ttk.Treeview(root, columns=columns, show="headings")

# Define structural headings
tree.heading("id", text="ID")
tree.heading("name", text="Name")
tree.heading("role", text="Role")

# Set exact column dimensions
tree.column("id", width=50, anchor=tk.CENTER)
tree.column("name", width=150)
tree.column("role", width=150)

# Inject data rows
users = [
    (1, "Alice", "Developer"),
    (2, "Bob", "Designer"),
    (3, "Charlie", "Manager")
]
for user in users:
    tree.insert("", tk.END, values=user)

tree.pack(pady=20, fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", show_row_selected)

root.mainloop()
