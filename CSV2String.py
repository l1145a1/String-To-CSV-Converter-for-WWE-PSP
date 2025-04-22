import struct
import sys
import os
import csv

def csv_to_binary(input_csv):
    output_file = os.path.splitext(input_csv)[0] + ".dat"

    try:
        # Buka file CSV dengan mode binary untuk mempertahankan null characters
        with open(input_csv, "rb") as csvfile:
            # Baca seluruh konten
            raw_content = csvfile.read()

            # Decode dengan UTF-8 sambil menangani karakter null
            content = raw_content.decode('utf-8', errors='replace')

            # Proses parsing CSV
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

                # Dapatkan string value dalam bentuk bytes asli (termasuk null)
                original_bytes = row[2].encode('utf-8', errors='replace')

                # Temukan posisi null character dalam string
                null_positions = [i for i, c in enumerate(row[2]) if ord(c) == 0]

                # Rekonstruksi bytes dengan null characters
                value = bytearray()
                for i, b in enumerate(original_bytes):
                    if i in null_positions:
                        value.append(0)  # Pertahankan null
                    else:
                        value.append(b)

                data.append((string_id, bytes(value)))

        count = len(data)
        header_size = 8 + count * 16

        with open(output_file, "wb") as f:
            f.write(b"\x00" * 4)
            f.write(struct.pack("<I", count))

            string_data = b""
            current_offset = header_size

            for string_id, value in data:
                length = len(value)

                f.write(struct.pack("<I", current_offset))
                f.write(struct.pack("<I", length))
                f.write(struct.pack("<I", string_id))
                f.write(b"\x00" * 4)

                string_data += value + b"\x00"
                current_offset += length + 1

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
