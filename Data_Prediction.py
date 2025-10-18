import pandas as pd
import os
import datetime
import tkinter as tk
from tkinter import ttk

# Load Excel Data
data_file_path = r'C:\Users\window\OneDrive\Desktop\data.xlsx'
df = pd.read_excel(data_file_path)

# Strip extra spaces from column names
df.columns = df.columns.str.strip()

# Extract relevant data based on actual dataset structure
thickness_options = df.filter(like="Thick_num_").dropna().values.flatten().astype(str).tolist()
material_options = df["Material Name"].dropna().astype(str).tolist() if "Material Name" in df.columns else []
orientation_options = df["Ply Orientation"].dropna().astype(str).tolist() if "Ply Orientation" in df.columns else []

# Remove potential 'NaN' values
thickness_options = [val for val in thickness_options if val and val.lower() != "nan"]
material_options = [val for val in material_options if val and val.lower() != "nan"]
orientation_options = [val for val in orientation_options if val and val.lower() != "nan"]

# Ensure dropdowns are not empty
if not thickness_options:
    thickness_options = ["0.086", "Variable"]
if not material_options:
    material_options = ["ZeroFiberLayer", "CarbonFiber"]
if not orientation_options:
    orientation_options = ["-90", "-45", "-30", "15", "30", "45", "90"]

# Define default ply names based on input count
ply_defaults = {
    2: ["TopPly", "BotPly"],
    3: ["TopPly", "Ply1", "BotPly"],
    4: ["TopPly", "Ply1", "Ply2", "BotPly"],
    5: ["TopPly", "Ply1", "Ply2", "Ply3", "BotPly"]
}

# Create GUI window
root = tk.Tk()
root.title("Select Input from Dropdown")

# Variable for the range of inputs (2, 3, 4, 5)
num_entries_var = tk.StringVar(value="2")

# Function to save inputs
def save_input():
    num_entries = int(num_entries_var.get())
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.expanduser(f'~/Desktop/user_input_{timestamp}.txt')
    
    selected_values = []
    for i in range(num_entries):
        selected_values.append(
            f"{thickness_vars[i].get()},{integration_vars[i].get()},{material_vars[i].get()},{orientation_vars[i].get()},{ply_defaults[num_entries][i]}"
        )

    # Save user input to a new text file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(selected_values))

    print(f"User input saved successfully in {output_file_path}")
    os.startfile(output_file_path)

# Dropdown for selecting number of entries (2, 3, 4, 5)
ttk.Label(root, text="Select Number of Inputs (2-5):").grid(row=0, column=0)
ttk.Combobox(root, textvariable=num_entries_var, values=["2", "3", "4", "5"]).grid(row=0, column=1)

# Create lists to store dropdown variables
thickness_vars, integration_vars, material_vars, orientation_vars = [], [], [], []

# Function to dynamically generate input fields
def update_fields():
    num_entries = int(num_entries_var.get())

    # Clear existing fields
    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) > 0:
            widget.destroy()

    for i in range(num_entries):
        thickness_vars.append(tk.StringVar())
        integration_vars.append(tk.StringVar(value="3"))  # Default integration value
        material_vars.append(tk.StringVar())
        orientation_vars.append(tk.StringVar())

        ttk.Label(root, text=f"Entry {i+1} - Thickness:").grid(row=i+1, column=0)
        ttk.Combobox(root, textvariable=thickness_vars[i], values=thickness_options).grid(row=i+1, column=1)

        ttk.Label(root, text="Number of Integration:").grid(row=i+1, column=2)
        ttk.Combobox(root, textvariable=integration_vars[i], values=["3", "5"]).grid(row=i+1, column=3)

        ttk.Label(root, text="Material:").grid(row=i+1, column=4)
        ttk.Combobox(root, textvariable=material_vars[i], values=material_options).grid(row=i+1, column=5)

        ttk.Label(root, text="Orientation:").grid(row=i+1, column=6)
        ttk.Combobox(root, textvariable=orientation_vars[i], values=orientation_options).grid(row=i+1, column=7)

        ttk.Label(root, text=f"Ply Name: {ply_defaults[num_entries][i]}").grid(row=i+1, column=8)

    ttk.Button(root, text="Submit", command=save_input).grid(row=num_entries+1, columnspan=9)

# Update fields when the number of inputs changes
num_entries_var.trace("w", lambda *args: update_fields())
# Initialize fields
update_fields()

# Run the GUI
root.mainloop()
