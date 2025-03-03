import os
import subprocess

# Pastikan folder "data" ada
data_dir = "data"  
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Konfigurasi path output
data_file = os.path.join(data_dir, "tweets_walikota_kediri.csv")

# Gunakan format path Unix-style untuk kompatibilitas dengan Node.js
data_file = data_file.replace("\\", "/")

# Konfigurasi parameter
search_keyword = "kota kediri since:2024-12-03 until:2025-03-03 lang:id"
limit = 200
token = "6d0094544ee48e738c7ff314f88ee2a899e1e8e0"

# Path ke script TypeScript
script_path = os.path.abspath("tweet-harvest-main/src/bin.ts")
script_path = script_path.replace("\\", "/")  # Gunakan format yang aman

# Cek path sebelum dieksekusi
print(f"Script path: {script_path}")
print(f"Output file path: {data_file}")

# Jalankan `tweet-harvest`
cmd = f'npx ts-node "{script_path}" -o "{data_file}" -s "{search_keyword}" -l {limit} --token "{token}"'
subprocess.run(cmd, shell=True, check=True)
