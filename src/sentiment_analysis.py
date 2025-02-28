import pandas as pd
import re
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from deep_translator import GoogleTranslator

nltk.download('vader_lexicon')

# Load dataset
df = pd.read_csv('data/tweets_walikota_kediri.csv')  # Nama file csv

# Preprocessing: Bersih2
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

# Statistik Sentimen
sentiment_counts = df['sentiment'].value_counts()

# Visualisasi
plt.figure(figsize=(6,6))
plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=['green', 'grey', 'red'])
plt.title('Distribusi Sentimen')
plt.show()

# Simpan hasil
output_file = 'data/hasil_sentimen.csv'
df.to_csv(output_file, index=False)
print(f'Hasil analisis sentimen disimpan di {output_file}')
