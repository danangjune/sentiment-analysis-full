import pandas as pd
import re
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')

# Load dataset
df = pd.read_csv('data/tweets_walikota_kediri.csv')

# Inisialisasi stopwords, tokenizer, dan lemmatizer
stop_words = set(stopwords.words('indonesian') + stopwords.words('english'))
custom_stopwords = {'walikota', 'kediri', 'pak', 'bu', 'mas', 'mbak', 'iya', 'nih', 'sih', 'kan', 'dong'}
additional_stopwords = {
    'kota', 'wali', 'wakil', 'prameswati', 'zanariah', 'selamat', 'periode', 'terpilih', 
    'muda', 'program', 'kepala', 'daerah', 'indonesia', 'pemerintah', 'seluruh', 'sampai', 'rakyat'
}
stop_words.update(custom_stopwords)
stop_words.update(additional_stopwords)

lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'\w+')

# Fungsi Preprocessing
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # Hapus URL
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)  # Hapus mention
    text = re.sub(r'#[A-Za-z0-9_]+', '', text)  # Hapus hashtag
    text = re.sub(r'[^a-zA-Z ]', '', text)  # Hapus karakter spesial & angka
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebih
    
    words = tokenizer.tokenize(text.lower())
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words and len(word) > 2]
    
    return ' '.join(words)

# Terapkan preprocessing ke semua tweet
df['clean_text'] = df['full_text'].astype(str).apply(clean_text)

# === 1. TF-IDF untuk ekstraksi topik utama ===
vectorizer = TfidfVectorizer(
    max_df=0.7,  
    min_df=3,    
    stop_words=list(stop_words)
)
tfidf_matrix = vectorizer.fit_transform(df['clean_text'])
feature_names = vectorizer.get_feature_names_out()

# Ambil 10 kata dengan skor tertinggi
tfidf_scores = tfidf_matrix.sum(axis=0).A1
top_indices = tfidf_scores.argsort()[-10:][::-1]  

# Filter kata yang tidak relevan
list_terlarang = {'selamat', 'terpilih', 'prameswati', 'zanariah', 'muda', 'periode'}
top_words = [feature_names[i] for i in top_indices if feature_names[i] not in list_terlarang and len(feature_names[i]) > 3]
top_scores = [tfidf_scores[i] for i in top_indices if feature_names[i] not in list_terlarang and len(feature_names[i]) > 3]

print("Topik utama dalam tweet (single-word):", top_words)

# === 2. Ekstraksi N-grams untuk mendapatkan frasa ===
vectorizer_ngram = CountVectorizer(
    ngram_range=(2,3),  
    max_df=0.8,  
    min_df=2,    
    stop_words=list(stop_words)
)
X_ngram = vectorizer_ngram.fit_transform(df['clean_text'])

# Ambil top-N frasa yang sering muncul
sum_words_ngram = X_ngram.sum(axis=0)
words_freq_ngram = [(word, sum_words_ngram[0, idx]) for word, idx in vectorizer_ngram.vocabulary_.items()]
words_freq_ngram = sorted(words_freq_ngram, key=lambda x: x[1], reverse=True)

# Ambil 10 frasa teratas
top_ngrams = [word for word, freq in words_freq_ngram[:10]]

print("Topik utama dalam tweet (bigram/trigram):", top_ngrams)

# === 3. Membuat Word Cloud ===
wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stop_words).generate(' '.join(df['clean_text']))

# Menampilkan Word Cloud
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud - Topik dalam Tweet")
plt.show()

# === 4. Plot Bar Chart ===
plt.figure(figsize=(10,5))
sns.barplot(x=top_scores, y=top_words, palette="viridis")
plt.xlabel("Skor TF-IDF")
plt.ylabel("Topik")
plt.title("Topik Utama dalam Tweet (Single-word)")
plt.show()

plt.figure(figsize=(10,5))
ngram_labels, ngram_counts = zip(*words_freq_ngram[:10])
sns.barplot(x=ngram_counts, y=ngram_labels, palette="magma")
plt.xlabel("Frekuensi")
plt.ylabel("Topik (Bigram/Trigram)")
plt.title("Topik Utama dalam Tweet (Bigram/Trigram)")
plt.show()
