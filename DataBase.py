import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import csv
import xml.etree.ElementTree as ET
import openpyxl

class DatabaseManager:
    def __init__(self, db_name="mydatabase.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_table(self, table_name, columns):
        try:
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print(f"Table '{table_name}' created successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            return False

    def insert_data(self, table_name, data):
        try:
            placeholders = ', '.join(['?'] * len(data[0]))
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            self.cursor.executemany(insert_query, data)
            self.conn.commit()
            print(f"Data inserted into '{table_name}' successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            return False

    def update_data(self, table_name, set_clause, where_clause):
        try:
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            self.cursor.execute(update_query)
            self.conn.commit()
            print(f"Data updated in '{table_name}' successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error updating data: {e}")
            return False

    def delete_data(self, table_name, where_clause):
        try:
            delete_query = f"DELETE FROM {table_name} WHERE {where_clause}"
            self.cursor.execute(delete_query)
            self.conn.commit()
            print(f"Data deleted from '{table_name}' successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")
            return False

    def query_data(self, query):
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error querying data: {e}")
            return None

    def export_to_csv(self, table_name, filepath):
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            df.to_csv(filepath, index=False)
            print(f"Data exported to '{filepath}' successfully.")
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False

    def import_from_csv(self, table_name, filepath):
        try:
            df = pd.read_csv(filepath)
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
            print(f"Data imported from '{filepath}' successfully.")
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            return False

    def export_to_xml(self, table_name, filepath):
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            root = ET.Element("data")
            for index, row in df.iterrows():
                item = ET.SubElement(root, "item")
                for col in df.columns:
                    ET.SubElement(item, col).text = str(row[col])
            tree = ET.ElementTree(root)
            tree.write(filepath)
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False

    def import_from_xml(self, table_name, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            data = []
            for item in root.findall("item"):
                row = []
                for col in item.findall("*"):
                    row.append(col.text)
                data.append(tuple(row))
            self.insert_data(table_name, data)
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            return False

    def export_to_xlsx(self, table_name, filepath):
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            df.to_excel(filepath, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to excel: {e}")
            return False

    def import_from_xlsx(self, table_name, filepath):
        try:
            df = pd.read_excel(filepath)
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Error importing from excel: {e}")
            return False



    def visualize_data(self, query):
        try:
            df = pd.read_sql_query(query, self.conn)
            df.plot(kind='bar')
            plt.show()
            return True
        except Exception as e:
            print(f"Error visualizing data: {e}")
            return False



class DatabaseApp:
    def __init__(self, master, db_manager):
        self.master = master
        self.db_manager = db_manager
        master.title("Database Management System")
        self.create_widgets()

    def create_widgets(self):
        self.table_label = ttk.Label(self.master, text="Table Name:")
        self.table_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.table_entry = ttk.Entry(self.master)
        self.table_entry.grid(row=0, column=1, padx=5, pady=5)

        self.columns_frame = tk.Frame(self.master)
        self.columns_frame.grid(row=1, column=0, columnspan=2, pady=10)
        self.add_column_row()

        buttons_frame = tk.Frame(self.master)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)  # Adjust row as needed

        button_specs = [
            ("Create Table", self.create_table),
            ("Insert Data", self.insert_data),
            ("Update Data", self.update_data),
            ("Delete Data", self.delete_data),
        ]

        for i, (text, command) in enumerate(button_specs):
            button = ttk.Button(buttons_frame, text=text, command=command)
            button.grid(row=0, column=i, padx=5, pady=2, sticky=tk.EW)

        self.add_column_button = ttk.Button(self.master, text="+ Add Column", command=self.add_column_row)
        self.add_column_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.query_button = ttk.Button(self.master, text="Query Data", command=self.query_data)
        self.query_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.export_csv_button = ttk.Button(self.master, text="Export to CSV", command=self.export_csv)
        self.export_csv_button.grid(row=8, column=0, pady=5)

        self.import_csv_button = ttk.Button(self.master, text="Import from CSV", command=self.import_csv)
        self.import_csv_button.grid(row=8, column=1, pady=5)

        self.export_xml_button = ttk.Button(self.master, text="Export to XML", command=self.export_xml)
        self.export_xml_button.grid(row=9, column=0, pady=5)

        self.import_xml_button = ttk.Button(self.master, text="Import from XML", command=self.import_xml)
        self.import_xml_button.grid(row=9, column=1, pady=5)

        self.export_xlsx_button = ttk.Button(self.master, text="Export to XLSX", command=self.export_xlsx)
        self.export_xlsx_button.grid(row=10, column=0, pady=5)

        self.import_xlsx_button = ttk.Button(self.master, text="Import from XLSX", command=self.import_xlsx)
        self.import_xlsx_button.grid(row=10, column=1, pady=5)

        self.visualize_button = ttk.Button(self.master, text="Visualize Data", command=self.visualize_data)
        self.visualize_button.grid(row=11, column=0, columnspan=2, pady=10)

        # Output text area
        self.output_text = tk.Text(self.master, height=10, width=50)
        self.output_text.grid(row=13, column=0, columnspan=2, pady=10)

        # Query input
        self.query_label = ttk.Label(self.master, text="SQL Query:")
        self.query_label.grid(row=12, column=0, sticky=tk.W, padx=5, pady=5)
        self.query_entry = ttk.Entry(self.master, width=50)
        self.query_entry.grid(row=12, column=1, padx=5, pady=5)

    def add_column_row(self):
        row_num = len(self.columns_frame.winfo_children()) // 2
        col_name_label = ttk.Label(self.columns_frame, text=f"Column {row_num + 1} Name:")
        col_name_label.grid(row=row_num, column=0, sticky=tk.W, padx=5)
        col_name_entry = ttk.Entry(self.columns_frame)
        col_name_entry.grid(row=row_num, column=1, padx=5)
        col_type_label = ttk.Label(self.columns_frame, text=f"Column {row_num + 1} Type:")
        col_type_label.grid(row=row_num, column=2, sticky=tk.W, padx=5)
        col_type_entry = ttk.Entry(self.columns_frame)
        col_type_entry.grid(row=row_num, column=3, padx=5)
        self.columns_frame.update_idletasks()

    def get_column_definitions(self):
        num_rows = len(self.columns_frame.winfo_children()) // 2
        columns = []
        for i in range(num_rows):
            try:
                name_entry = self.columns_frame.grid_slaves(row=i, column=1)[0]
                type_entry = self.columns_frame.grid_slaves(row=i, column=3)[0]
                name = name_entry.get()
                type = type_entry.get()
                if name and type:
                    columns.append(f"{name} {type}")
            except IndexError:
                print(f"Warning: Skipping incomplete column row {i + 1}")
                continue
        return ", ".join(columns)

    def show_message(self, message, type="info"):
        if type == "info":
            messagebox.showinfo("Message", message)
        elif type == "error":
            messagebox.showerror("Error", message)

    def create_table(self):
        table_name = self.table_entry.get()
        columns = self.get_column_definitions()
        if not table_name or not columns:
            self.show_message("Please enter a table name and at least one column.", "error")
            return
        if self.db_manager.create_table(table_name, columns):
            self.show_message(f"Table '{table_name}' created successfully.")
        else:
            self.show_message("Error creating table.", "error")

    def insert_data(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        data = [(1,"Product X", 100, 10)]
        if self.db_manager.insert_data(table_name, data):
            self.show_message(f"Data inserted into '{table_name}' successfully.")
        else:
            self.show_message("Error inserting data.", "error")

    def update_data(self):
        pass

    def delete_data(self):
        pass

    def query_data(self):
        query = self.query_entry.get()
        if not query:
            self.show_message("Please enter an SQL query.", "error")
            return
        results = self.db_manager.query_data(query)
        if results:
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, str(results))
        else:
            self.show_message("No results found or query error.", "error")

    def export_csv(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            if self.db_manager.export_to_csv(table_name, filepath):
                self.show_message(f"Data exported to {filepath}")
            else:
                self.show_message("Error exporting data.", "error")

    def import_csv(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filepath:
            if self.db_manager.import_from_csv(table_name, filepath):
                self.show_message(f"Data imported from {filepath}")
            else:
                self.show_message("Error importing data.", "error")

    def export_xml(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if filepath:
            if self.db_manager.export_to_xml(table_name, filepath):
                self.show_message(f"Data exported to {filepath}")
            else:
                self.show_message("Error exporting data.", "error")

    def import_xml(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        filepath = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if filepath:
            if self.db_manager.import_from_xml(table_name, filepath):
                self.show_message(f"Data imported from {filepath}")
            else:
                self.show_message("Error importing data.", "error")

    def export_xlsx(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("XLSX files", "*.xlsx")])
        if filepath:
            if self.db_manager.export_to_xlsx(table_name, filepath):
                self.show_message(f"Data exported to {filepath}")
            else:
                self.show_message("Error exporting data.", "error")

    def import_xlsx(self):
        table_name = self.table_entry.get()
        if not table_name:
            self.show_message("Please enter a table name.", "error")
            return
        filepath = filedialog.askopenfilename(filetypes=[("XLSX files", "*.xlsx")])
        if filepath:
            if self.db_manager.import_from_xlsx(table_name, filepath):
                self.show_message(f"Data imported from {filepath}")
            else:
                self.show_message("Error importing data.", "error")

    def visualize_data(self):
        query = self.query_entry.get()
        if not query:
            self.show_message("Please enter an SQL query.", "error")
            return

        results = self.db_manager.query_data(query)
        if results:
            self.display_table_in_new_window(results, query)
        else:
            self.show_message("No results found or query error.", "error")

    def display_table_in_new_window(self, data, query):
        try:
            new_window = tk.Toplevel(self.master)
            new_window.title("Query Results")

            table_view = ttk.Treeview(new_window)
            table_view.pack(expand=True, fill=tk.BOTH)

            columns = [desc[0] for desc in self.db_manager.cursor.description]
            table_view["columns"] = columns
            table_view.heading("#0", text="")
            for col in columns:
                table_view.heading(col, text=col)
                table_view.column(col, anchor=tk.CENTER, width=100, stretch=True)

            for row in data:
                table_view.insert("", "end", values=row)

            new_window.update_idletasks()
            new_window.geometry("")

        except Exception as e:
            self.show_message(f"Error displaying table: {e}", "error")


root = tk.Tk()
root.geometry("800x600")
root.resizable(True, True)
db_manager = DatabaseManager()
app = DatabaseApp(root, db_manager)
root.mainloop()
db_manager.close()
