import os
import shutil
import hexeditor
import virustotal_python

# VirusTotal API key
API_KEY = "YOUR_API_KEY_HERE"

# Directory to scan
dir_to_scan = "path/to/directory"

# File size threshold
size_threshold = 100000000  # 100MB

# Hex editor library
hex_editor = hexeditor.HexEditor()

# Initialize VirusTotal API
virus_total = virustotal_python.VirusTotal(API_KEY)

# Iterate through all files in directory
for root, dirs, files in os.walk(dir_to_scan):
    for file in files:
        file_path = os.path.join(root, file)
        file_size = os.path.getsize(file_path)

        # Check if file size is greater than threshold
        if file_size > size_threshold:
            with open(file_path, "rb") as f:
                # Read first and last few bytes of the file
                first_bytes = f.read(8)
                f.seek(-8, os.SEEK_END)
                last_bytes = f.read(8)

                # Check if first and last bytes are filled with zeros
                if first_bytes == b"\x00" * 8 and last_bytes == b"\x00" * 8:
                    # Open file in hex editor
                    hex_editor.open_file(file_path)
                    # Search for script in the middle
                    script = hex_editor.search(b"\x3c\x73\x63\x72\x69\x70\x74")

                    # If script is found
                    if script:
                        # Copy script to new file
                        new_file_path = file_path + "_script"
                        shutil.copy(script, new_file_path)
                        # Scan new file with VirusTotal
                        scan_result = virus_total.scan_file(new_file_path)
                        print(f'{new_file_path} was scanned with VirusTotal and the result is {scan_result.status()}')
