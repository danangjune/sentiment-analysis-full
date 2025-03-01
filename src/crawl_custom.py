from flask import Flask, request, jsonify
import os
import subprocess
import re

app = Flask(__name__)

# Pastikan folder data ada
DATA_FOLDER = "../data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def sanitize_filename(keyword):
    """Membersihkan keyword agar valid untuk nama file."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", keyword.lower())

@app.route("/api/crawl", methods=["POST"])
def start_crawling():
    try:
        data = request.get_json()
        keyword = data.get("keyword")
        start_date = data.get("startDate")
        end_date = data.get("endDate")
        limit = data.get("limit", 100)  # Default limit 100

        if not keyword or not start_date or not end_date:
            return jsonify({"error": "Keyword dan tanggal harus diisi"}), 400

        clean_keyword = sanitize_filename(keyword)
        data_file = os.path.join(DATA_FOLDER, f"tweets_{clean_keyword}.csv")

        search_keyword = f'"{keyword} since:{start_date} until:{end_date} lang:id"'
        token = "6d0094544ee48e738c7ff314f88ee2a899e1e8e0"

        # Eksekusi tweet-harvest
        cmd = f'npx --yes tweet-harvest@2.6.1 -o "{data_file}" -s {search_keyword} -l {limit} --token "{token}"'
        subprocess.run(cmd, shell=True, check=True)

        return jsonify({"message": "Crawling selesai!", "file": data_file}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
