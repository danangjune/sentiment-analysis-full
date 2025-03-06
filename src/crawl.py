import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Mengizinkan semua origin

# Pastikan folder "data" ada
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Token API (sebaiknya simpan di environment variable)
TOKEN = "6d0094544ee48e738c7ff314f88ee2a899e1e8e0"

@app.route("/api/crawl", methods=["POST"])
def crawl():
    try:
        # Ambil data dari request JSON
        data = request.json
        keyword = data.get("keyword", "kota kediri")  # Default keyword
        start_date = data.get("startDate")  # Harus format YYYY-MM-DD
        end_date = data.get("endDate")  # Harus format YYYY-MM-DD
        limit = int(data.get("limit", 200))  # Default limit 200

        if not start_date or not end_date:
            return jsonify({"error": "Tanggal mulai dan akhir harus diisi"}), 400

        # Path output file
        data_file = os.path.join(DATA_DIR, "tweets_walikota_kediri.csv").replace("\\", "/")

        # Format query untuk tweet-harvest
        search_keyword = f"{keyword} since:{start_date} until:{end_date} lang:id"

        # Path ke script TypeScript
        script_path = os.path.abspath("tweet-harvest-main/src/bin.ts").replace("\\", "/")

        # Debugging print
        print(f"Executing: npx ts-node \"{script_path}\" -o \"{data_file}\" -s \"{search_keyword}\" -l {limit} --token \"{TOKEN}\"")

        # Jalankan tweet-harvest
        cmd = f'npx ts-node "{script_path}" -o "{data_file}" -s "{search_keyword}" -l {limit} --token "{TOKEN}"'
        subprocess.run(cmd, shell=True, check=True)

        return jsonify({"message": "Crawling started", "status": "success", "output": data_file}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Gagal menjalankan tweet-harvest: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)