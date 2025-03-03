from flask import Flask, jsonify
import pandas as pd
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from deep_translator import GoogleTranslator
from flask_cors import CORS
import math
import numpy as np

# Download lexicon untuk analisis sentimen
nltk.download('vader_lexicon')

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)  # Agar API bisa diakses dari frontend

# Load dataset dari CSV
CSV_PATH = 'tweets-data/data/tweets_walikota_kediri.csv'
try:
    df = pd.read_csv(CSV_PATH, parse_dates=['created_at'])
except FileNotFoundError:
    print(f"Error: File '{CSV_PATH}' tidak ditemukan!")
    df = pd.DataFrame(columns=["full_text", "created_at", "favorite_count", "retweet_count", "conversation_id_str", "user_id_str", "username", "tweet_url", "image_url"]) 

# Fungsi untuk membersihkan teks tweet
def clean_text(text):
    text = re.sub(r'http\S+', ' ', text)  # Hapus URL
    text = re.sub(r'@[A-Za-z0-9_]+', ' ', text)  # Hapus mention
    text = re.sub(r'#[A-Za-z0-9_]+', ' ', text)  # Hapus hashtag
    text = re.sub(r'[^a-zA-Z ]', '', text)  # Hapus karakter spesial & angka
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebih
    return text.lower()

df['clean_text'] = df['full_text'].astype(str).apply(clean_text)

# Translate teks ke bahasa Inggris sebelum analisis sentimen
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
        return 'positive'
    elif score['compound'] <= -0.05:
        return 'negative'
    else:
        return 'neutral'

df['sentiment'] = df['translated_text'].apply(get_sentiment)

# Hitung jumlah sentimen positif, negatif, dan netral
sentiment_counts = df['sentiment'].value_counts().to_dict()

# Hitung tren sentimen berdasarkan tanggal
df['date'] = df['created_at'].dt.date
sentiment_trend = df.groupby(['date', 'sentiment']).size().unstack().fillna(0)

# Hitung total engagement (retweet + favorite)
df['engagement'] = df['favorite_count'] + df['retweet_count']

# Ambil tweet dengan engagement tertinggi (top 5)
top_tweets = df.nlargest(10, 'engagement')[['conversation_id_str', 'created_at', 'full_text', 'favorite_count', 'user_id_str', 'username', 'image_url', 'retweet_count', 'tweet_url']].to_dict(orient='records')

# Hitung total tweet dan rata-rata engagement
total_tweets = len(df)
average_engagement = df['engagement'].mean() if total_tweets > 0 else 0
total_engagement = df['engagement'].sum()

# Hitung sentimen
positive_count = sentiment_counts.get("positive", 0)
negative_count = sentiment_counts.get("negative", 0)
neutral_count = sentiment_counts.get("neutral", 0)

# Konversi data tren sentimen ke format JSON
time_series_data = [
    {
        "date": str(date),
        "positive": int(row.get("positive", 0)),
        "negative": int(row.get("negative", 0)),
        "neutral": int(row.get("neutral", 0))
    }
    for date, row in sentiment_trend.iterrows()
]

@app.route('/api/sentiment/summary', methods=['GET'])
def get_summary():
    tweets = df[['full_text', 'created_at', 'username', 'tweet_url']].fillna("").to_dict(orient='records')

    # Gganti NaN dengan nilai yang valid
    def safe_int(value):
        return int(value) if isinstance(value, (int, float)) and not math.isnan(value) else 0

    def clean_json(data):
        if isinstance(data, dict):
            return {key: clean_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [clean_json(item) for item in data]
        elif isinstance(data, float) and np.isnan(data):
            return None  # Ganti NaN dengan None
        return data

    # Buat response JSON
    response = {
        "tweets": tweets,
        "sentimentBreakdown": {
            "positive": safe_int(positive_count),
            "negative": safe_int(negative_count),
            "neutral": safe_int(neutral_count)
        },
        "timeSeriesData": time_series_data,
        "topTweets": top_tweets,
        "totalTweets": safe_int(total_tweets),
        "totalEngagement": int(total_engagement),
        "averageEngagement": safe_int(average_engagement)
    }

    # Pastikan JSON bersih dari NaN
    response = clean_json(response)

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

output_file = 'data/hasil_sentimen.csv'
df.to_csv(output_file, index=False)