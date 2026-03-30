import os
import csv

# 📁 Folder where your .txt files are stored
folder_path = "/Users/agsen/Desktop/essbase/calc_reference"

# 📄 CSV output file
output_file = "/Users/agsen/Desktop/combined2.csv"

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["FUNC_NAME", "CONTENT"])  # Header row

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            func_name = os.path.splitext(filename)[0]  # removes '.txt'
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().replace("\0", "")  # clean any null characters
            writer.writerow([func_name, content])

print(f"✅ Finished! CSV saved at: {os.path.abspath(output_file)}")
