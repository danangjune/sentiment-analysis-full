import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from deep_translator import GoogleTranslator

nltk.download('vader_lexicon')

# Load dataset
df = pd.read_csv('data/tweets_walikota_kediri.csv')  # Ganti dengan nama file csv kamu

# Konversi 'created_at' ke format datetime
df['created_at'] = pd.to_datetime(df['created_at'])

# Preprocessing: Bersih2
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # Hapus URL
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)  # Hapus mention
    text = re.sub(r'#[A-Za-z0-9_]+', '', text)  # Hapus hashtag
    text = re.sub(r'[^a-zA-Z ]', '', text)  # Hapus karakter spesial & angka
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebih
    return text.lower()

df['clean_text'] = df['full_text'].astype(str).apply(clean_text)

# Fungsi Terjemahan
def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text  # Kalau gagal, tetap pakai teks asli

df['translated_text'] = df['clean_text'].apply(translate_text)  # Translasi sebelum analisis sentimen

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

df['sentiment'] = df['translated_text'].apply(get_sentiment)  # Gunakan teks yang sudah diterjemahkan

# Kelompokkan berdasarkan tanggal dan sentimen
df['date'] = df['created_at'].dt.date  # Ambil hanya tanggal
sentiment_trend = df.groupby(['date', 'sentiment']).size().unstack().fillna(0)

# Plot Line Chart
plt.figure(figsize=(10, 5))
sns.lineplot(data=sentiment_trend, marker="o")
plt.title("Tren Sentimen Wali Kota Kediri dari Waktu ke Waktu")
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Tweet")
plt.xticks(rotation=45)
plt.legend(title="Sentimen")
plt.show()
