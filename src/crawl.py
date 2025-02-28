import os
import pandas as pd
import subprocess

# Pastikan folder data ada
if not os.path.exists("../data"):
    os.makedirs("../data")

# Konfigurasi
data_file = "../data/tweets_walikota_kediri.csv"
search_keyword = "walikota kediri since:2024-01-27 until:2025-02-27 lang:id"  # Cari tweet terbaru
limit = 50 # Batasi jumlah tweet agar cepat
token = "6d0094544ee48e738c7ff314f88ee2a899e1e8e0"  # Token dari cookies

# Eksekusi tweet-harvest
cmd = f'npx --yes tweet-harvest@2.6.1 -o "{data_file}" -s "{search_keyword}" -l {limit} --token "{token}"'
subprocess.run(cmd, shell=True, check=True)

# Baca hasil crawling
data_file = os.path.abspath("data/tweets_walikota_kediri.csv")
df = pd.read_csv(data_file, sep=",")

# Tampilkan info + 5 tweet pertama
print(df.info())
print(df.head(5))  # Cuma tampilkan 5 tweet pertama
