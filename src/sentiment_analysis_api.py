from flask import Flask, jsonify
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
CSV_PATH = 'data/tweets_walikota_kediri.csv' 
try:
    df = pd.read_csv(CSV_PATH, parse_dates=['created_at']) 
except FileNotFoundError:
    print(f"Error: File '{CSV_PATH}' tidak ditemukan!")
    df = pd.DataFrame(columns=["full_text", "created_at"]) 

# Preprocessing: Membersihkan teks
def clean_text(text):
    text = re.sub(r'http\S+', ' ', text)  # Hapus URL
    text = re.sub(r'@[A-Za-z0-9_]+', ' ', text)  # Hapus mention
    text = re.sub(r'#[A-Za-z0-9_]+', ' ', text)  # Hapus hashtag
    text = re.sub(r'[^a-zA-Z ]', '', text)  # Hapus karakter spesial & angka
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebih
    return text.lower()

df['clean_text'] = df['full_text'].astype(str).apply(clean_text)

# Translate ke Bahasa Inggris sebelum Sentimen
def translate_text(text):
    try:
        return GoogleTranslator(source='id', target='en').translate(text)
    except:
        return text 

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

# Hitung jumlah masing-masing sentimen untuk diagram donat
sentiment_counts = df['sentiment'].value_counts().to_dict()

# Hitung tren sentimen per tanggal
df['date'] = df['created_at'].dt.date  # Ambil hanya tanggal
sentiment_trend = df.groupby(['date', 'sentiment']).size().unstack().fillna(0)

# ---------------------------- API ENDPOINTS ----------------------------

# Cek apakah API berjalan
@app.route('/api/sentiment', methods=['GET'])
def sentiment_analysis():
    return jsonify({"message": "API Sentimen Berjalan"})

# Endpoint untuk data diagram donat (Total Sentimen)
@app.route('/api/sentiment/data', methods=['GET'])
def get_sentiment_data():
    return jsonify(sentiment_counts)

# Endpoint untuk tren sentimen (Time Series)
@app.route('/api/sentiment/trend', methods=['GET'])
def get_sentiment_trend():
    # Pastikan kolom created_at sudah dalam format datetime
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Ambil hanya tanggal dari created_at
    df['date'] = df['created_at'].dt.date  

    # Kelompokkan sentimen berdasarkan tanggal
    sentiment_trend = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)

    # Konversi indeks (tanggal) ke string agar bisa di-serialize ke JSON
    trend_data = {str(date): row.to_dict() for date, row in sentiment_trend.iterrows()}

    return jsonify(trend_data)

# Jalankan API
if __name__ == '__main__':
    app.run(debug=True)
