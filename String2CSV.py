import struct
import sys
import os
import csv

def read_string(f):
    count = 0  # Offset 4
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
        f.read(4)  # Skip 4 bytes (padding or unused data)

    # Read actual strings
    for i in range(count):
        f.seek(string_offset[i])
        value = f.read(string_length[i]).decode('utf-8', errors='ignore')
        string_data.append((string_id[i], string_length[i], value))

    return string_data

def convert_to_csv(input_file):
    output_file = os.path.splitext(input_file)[0] + ".csv"

    try:
        with open(input_file, "rb") as f:
            data = read_string(f)

        with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["ID", "Length", "Value"])
            writer.writerows(data)

        print(f"Conversion successful! CSV saved as: {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if os.path.isfile(input_file):
        convert_to_csv(input_file)
    else:
        print(f"File not found: {input_file}")
