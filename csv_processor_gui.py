import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as ttk
import csv
import re


class CSVProcessor:
    def __init__(self, master):

        self.csv_window = tk.Toplevel(master)
        self.csv_window.title("CSV Processing")
        self.csv_window.geometry("1000x1000")
        self.csv_window.iconbitmap("images/logo.ico")
        self.csv_window.protocol("WM_DELETE_WINDOW", self.csv_window.destroy)

        self.create_input_frame()
        self.create_viewer_frame()

        self.data = []

    def create_input_frame(self):
        input_frame_csv = ttk.LabelFrame(self.csv_window, text="CSV Parsing")
        input_frame_csv.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame_csv, text="Parsed Text File Input").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.url_file_entry = ttk.Entry(input_frame_csv, width=50)
        self.url_file_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame_csv,
            bootstyle="success",
            text="Browse",
            command=self.browse_csv_file,
        ).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(input_frame_csv, text="Output File:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.output_file_entry = ttk.Entry(input_frame_csv, width=50)
        self.output_file_entry.grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame_csv, bootstyle="success", text="Save As", command=self.save_as
        ).grid(row=4, column=2, padx=5, pady=5)

        ttk.Button(input_frame_csv, text="Process", command=self.process_csv).grid(
            row=5, column=1, padx=5, pady=5
        )

    def create_viewer_frame(self):
        viewer_frame = ttk.LabelFrame(self.csv_window, text="Viewer")
        viewer_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(viewer_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            viewer_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = ttk.Frame(self.csv_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Add Row", command=self.add_row).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Delete Row", command=self.delete_row).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(
            side="left", padx=5
        )

    def browse_csv_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.url_file_entry.delete(0, tk.END)
        self.url_file_entry.insert(0, file)

    def save_as(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if file:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file)

    def process_csv(self):
        input_file = self.url_file_entry.get()
        output_file = self.output_file_entry.get()

        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select both input and output files.")
            return

        try:
            self.data = self.process_file(input_file)
            if self.data:
                self.export_to_csv(self.data, output_file)

                self.display_data()
            else:
                messagebox.showwarning(
                    "Warning", "No data was extracted from the input file."
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_data(self):
        self.tree.delete(*self.tree.get_children())
        if not self.data:
            return

        columns = list(self.data[0].keys())
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(
                col, width=ttk.font.Font().measure(col) + 20
            )  # Adjust width based on column text

        for row in self.data:
            self.tree.insert("", "end", values=list(row.values()))

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        column_index = int(column[1:]) - 1
        column_name = self.tree["columns"][column_index]

        current_value = self.tree.item(item, "values")[column_index]
        new_value = simpledialog.askstring(
            "Edit", f"Edit {column_name}", initialvalue=current_value
        )

        if new_value is not None:
            values = list(self.tree.item(item, "values"))
            values[column_index] = new_value
            self.tree.item(item, values=values)

            row_index = self.tree.index(item)
            self.data[row_index][column_name] = new_value

    def add_row(self):
        new_row = {col: "" for col in self.tree["columns"]}
        self.data.append(new_row)
        self.tree.insert("", "end", values=list(new_row.values()))

    def delete_row(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item[0])
            self.tree.delete(selected_item[0])
            del self.data[index]
        else:
            messagebox.showwarning("Warning", "Please select a row to delete.")

    def save_changes(self):
        output_file = self.output_file_entry.get()
        if output_file:
            self.export_to_csv(self.data, output_file)
            messagebox.showinfo("Success", f"Changes saved to '{output_file}'.")
        else:
            messagebox.showerror("Error", "Please specify an output file.")

    def process_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()

        entries = contents.split("==================================================")

        data = []
        for entry in entries:
            if entry.strip():
                entry_info = self.extract_info_from_text(entry.strip())
                data.append(entry_info)

        return data

    def extract_info_from_text(self, text):
        result = {}

        image_match = re.search(r"Image (\d+)", text)
        if image_match:
            result["Image Number"] = image_match.group(1)

        url_match = re.search(r"URL: (.+)", text)
        if url_match:
            result["URL"] = url_match.group(1)

        fields = [
            "verbatimCollectors",
            "collectedBy",
            "secondaryCollectors",
            "recordNumber",
            "verbatimEventDate",
            "minimumEventDate",
            "maximumEventDate",
            "verbatimIdentification",
            "latestScientificName",
            "identifiedBy",
            "verbatimDateIdentified",
            "associatedTaxa",
            "country",
            "firstPoliticalUnit",
            "secondPoliticalUnit",
            "municipality",
            "verbatimLocality",
            "locality",
            "habitat",
            "verbatimElevation",
            "verbatimCoordinates",
            "otherCatalogNumbers",
            "originalMethod",
            "typeStatus",
        ]

        for field in fields:
            match = re.search(rf"{field}: (.+)", text)
            if match:
                result[field] = match.group(1)
            else:
                result[field] = "N/A"

        return result

    def export_to_csv(self, data, csv_file_path):
        if not data:
            raise ValueError("No data to write to CSV.")

        fields = list(data[0].keys())
        with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
