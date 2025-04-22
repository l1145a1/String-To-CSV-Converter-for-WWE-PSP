import struct
import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class StringConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("String Converter")
        self.root.geometry("500x300")

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="String File Converter", font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Conversion type selection
        self.conversion_type = tk.StringVar(value="csv_to_binary")
        ttk.Radiobutton(
            main_frame,
            text="CSV to Binary (.dat)",
            variable=self.conversion_type,
            value="csv_to_binary"
        ).pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(
            main_frame,
            text="Binary (.dat) to CSV",
            variable=self.conversion_type,
            value="binary_to_csv"
        ).pack(anchor=tk.W, pady=5)

        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=15)

        ttk.Label(file_frame, text="Input File:").pack(anchor=tk.W)

        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=40)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Convert button
        convert_btn = ttk.Button(
            main_frame,
            text="Convert",
            command=self.convert_file,
            style='Accent.TButton'
        )
        convert_btn.pack(pady=20)

        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground='green')
        self.status_label.pack()

        # Configure styles
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

    def browse_file(self):
        filetypes = []
        if self.conversion_type.get() == "csv_to_binary":
            filetypes = [("CSV Files", "*.csv"), ("All Files", "*.*")]
        else:
            filetypes = [("Binary Files", "*.dat"), ("All Files", "*.*")]

        filename = filedialog.askopenfilename(
            title="Select input file",
            filetypes=filetypes
        )

        if filename:
            self.file_path.set(filename)

    def convert_file(self):
        input_file = self.file_path.get()

        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return

        if not os.path.isfile(input_file):
            messagebox.showerror("Error", f"File not found: {input_file}")
            return

        try:
            if self.conversion_type.get() == "csv_to_binary":
                output_file = os.path.splitext(input_file)[0] + ".dat"
                self.csv_to_binary(input_file, output_file)
            else:
                output_file = os.path.splitext(input_file)[0] + ".csv"
                self.binary_to_csv(input_file, output_file)

            self.status_label.config(text=f"Conversion successful!\nOutput: {output_file}", foreground='green')
            messagebox.showinfo("Success", f"File converted successfully!\nSaved as: {output_file}")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground='red')
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

    def csv_to_binary(self, input_csv, output_file):
        try:
            # Open CSV file in binary mode to preserve null characters
            with open(input_csv, "rb") as csvfile:
                # Read raw content and decode with null character handling
                raw_content = csvfile.read()
                content = raw_content.decode('utf-8', errors='replace')

                # Process CSV content
                lines = content.splitlines()
                reader = csv.reader(lines, delimiter=';')
                next(reader)  # Skip header row

                data = []
                for row in reader:
                    if len(row) < 3:
                        continue

                    try:
                        string_id = int(row[0])
                    except ValueError:
                        continue

                    # Get string value as bytes (preserving nulls)
                    original_bytes = row[2].encode('utf-8', errors='replace')

                    # Find null character positions in the string
                    null_positions = [i for i, c in enumerate(row[2]) if ord(c) == 0]

                    # Reconstruct bytes with null characters
                    value = bytearray()
                    for i, b in enumerate(original_bytes):
                        if i in null_positions:
                            value.append(0)  # Preserve null
                        else:
                            value.append(b)

                    data.append((string_id, bytes(value)))

            count = len(data)
            header_size = 8 + count * 16  # 4 empty + 4 count + (16 per string header)

            with open(output_file, "wb") as f:
                # Write file header
                f.write(b"\x00" * 4)  # Empty header
                f.write(struct.pack("<I", count))  # String count

                # Write string headers and collect data
                string_data = b""
                current_offset = header_size

                for string_id, value in data:
                    length = len(value)

                    # Write string header
                    f.write(struct.pack("<I", current_offset))  # Offset
                    f.write(struct.pack("<I", length))        # Length
                    f.write(struct.pack("<I", string_id))     # ID
                    f.write(b"\x00" * 4)                     # Padding

                    # Add string to data block
                    string_data += value + b"\x00"
                    current_offset += length + 1  # +1 for null terminator

                # Write all string data
                f.write(string_data)

            return True, f"Conversion successful! Binary saved as: {output_file}"
        except Exception as e:
            return False, f"Error: {e}"

    def binary_to_csv(self, input_file, output_file):
        with open(input_file, "rb") as f:
            data = self.read_binary_strings(f)

        with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["ID", "Length", "Value"])
            writer.writerows(data)

    def read_binary_strings(self, f):
        count = 0
        string_offset = []
        string_length = []
        string_id = []
        string_data = []

        # Read count
        f.seek(4)
        count = struct.unpack('<I', f.read(4))[0]

        # Read string headers
        for _ in range(count):
            offset = struct.unpack('<I', f.read(4))[0]
            string_offset.append(offset)
            length = struct.unpack('<I', f.read(4))[0]
            string_length.append(length)
            id_ = struct.unpack('<I', f.read(4))[0]
            string_id.append(id_)
            f.read(4)  # Skip 4 bytes (padding)

        # Read actual strings
        for i in range(count):
            f.seek(string_offset[i])
            value = f.read(string_length[i]).decode('utf-8', errors='ignore')
            string_data.append((string_id[i], string_length[i], value))

        return string_data

if __name__ == "__main__":
    root = tk.Tk()
    app = StringConverterApp(root)
    root.mainloop()
