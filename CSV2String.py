import struct
import sys
import os
import csv

def csv_to_binary(input_csv):
    output_file = os.path.splitext(input_csv)[0] + ".dat"

    try:
        with open(input_csv, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Skip header row
            data = [(int(row[0]), row[2].encode("utf-8")) for row in reader]

        count = len(data)
        header_size = 8 + count * 16  # 4 bytes kosong + 4 bytes count + (16 bytes per string header)

        with open(output_file, "wb") as f:
            # Tulis 4 bytes kosong
            f.write(b"\x00" * 4)
            # Tulis count dalam format little endian
            f.write(struct.pack("<I", count))

            # Tulis header dan kumpulkan string data
            string_data = b""
            current_offset = header_size

            for string_id, value in data:
                length = len(value)

                # Tulis header untuk string ini
                f.write(struct.pack("<I", current_offset))  # Offset
                f.write(struct.pack("<I", length))          # Length
                f.write(struct.pack("<I", string_id))       # ID
                f.write(b"\x00" * 4)                       # 4 bytes kosong

                # Tambahkan string ke data
                string_data += value + b"\x00"
                current_offset += length + 1  # +1 untuk null terminator

            # Tulis semua string data setelah header
            f.write(string_data)

        print(f"Conversion successful! Binary saved as: {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>")
        sys.exit(1)

    input_csv = sys.argv[1]
    if os.path.isfile(input_csv):
        csv_to_binary(input_csv)
    else:
        print(f"File not found: {input_csv}")
