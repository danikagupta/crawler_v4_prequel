import pandas as pd
import shutil
from pathlib import Path

# --- Input paths ---
csv_path = "Paper_selection_from_scoring - allscores_selected.csv"              # your CSV file
dir1 = Path("pdf_txt")  # directory containing original files
dir2 = Path("pdf_txt_selected")    # directory to copy files into

# --- Read CSV into a DataFrame ---
df = pd.read_csv(csv_path)

# Expect the CSV to have a column such as "filename"
# Example CSV:
# filename
# file1.txt
# file2.pdf
# file3.jpg

# --- Copy loop ---

copied_file_list=[]
missing_file_list=[]
i=0
for filename in df['filename']:
    src = dir1 / filename
    dst = dir2 / filename

    # Create dest directory if needed
    dir2.mkdir(parents=True, exist_ok=True)

    # Copy file
    i=i+1
    try:
        shutil.copy2(src, dst)
        print(f"{i}. Copied: {src} → {dst}")
        copied_file_list.append(filename)
    except FileNotFoundError:
        print(f"{i}. Missing file: {src}")
        missing_file_list.append(filename)
print(f"File counts: {len(copied_file_list)=}, {len(missing_file_list)=}")