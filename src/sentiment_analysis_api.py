from flask import Flask, jsonify, request
import pandas as pd
import re
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from deep_translator import GoogleTranslator
from flask_cors import CORS

nltk.download('vader_lexicon')

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)  # Agar bisa diakses dari frontend (React)

# Load dataset
CSV_PATH = 'data/tweets_walikota_kediri.csv'  # Pastikan file ini ada
try:
    df = pd.read_csv(CSV_PATH)  
except FileNotFoundError:
    print(f"Error: File '{CSV_PATH}' tidak ditemukan!")
    df = pd.DataFrame(columns=["full_text"])  # Buat DataFrame kosong jika tidak ada file

# Preprocessing: Membersihkan teks
def clean_text(text):
    text = re.sub(r'http\S+', ' ', text)  # Hapus URL
    text = re.sub(r'@[A-Za-z0-9_]+', ' ', text)  # Hapus mention
    text = re.sub(r'#[A-Za-z0-9_]+', ' ', text)  # Hapus hashtag
    text = re.sub(r'[^a-zA-Z ]', '', text)  # Hapus karakter spesial & angka
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebih
    return text.lower()

df['clean_text'] = df['full_text'].astype(str).apply(clean_text)

# Translasi ke Bahasa Inggris sebelum Sentimen
def translate_text(text):
    try:
        return GoogleTranslator(source='id', target='en').translate(text)
    except:
        return text  # Jika error, tetap gunakan teks asli

df['translated_text'] = df['clean_text'].apply(translate_text)

# Analisis Sentimen
sia = SentimentIntensityAnalyzer()

def get_sentiment(text):
    score = sia.polarity_scores(text)
    if score['compound'] >= 0.05:
        return 'Positif'
    elif score['compound'] <= -0.05:
        return 'Negatif'
    else:
        return 'Netral'

df['sentiment'] = df['translated_text'].apply(get_sentiment)

# Hitung jumlah masing-masing sentimen
sentiment_counts = df['sentiment'].value_counts().to_dict()

# Endpoint API: Cek apakah API berjalan
@app.route('/api/sentiment', methods=['GET', 'POST'])
def sentiment_analysis():
    return jsonify({"message": "API Sentimen Berjalan"})

# Endpoint API untuk data sentimen
@app.route('/api/sentiment/data', methods=['GET'])
def get_sentiment_data():
    return jsonify(sentiment_counts)

if __name__ == '__main__':
    app.run(debug=True)
