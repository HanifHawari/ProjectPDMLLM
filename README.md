# FitMind AI 🏋️‍♂️🧠

**FitMind AI** adalah platform kebugaran dan nutrisi berbasis Kecerdasan Buatan (AI) yang dirancang untuk membantu Anda mencapai tubuh impian. Dengan memanfaatkan model LLM mutakhir, FitMind AI menyajikan program latihan yang dipersonalisasi dan rekomendasi nutrisi cerdas yang disesuaikan dengan kondisi, preferensi, dan target kebugaran Anda.

---

## ✨ Fitur Unggulan

- 🤖 **AI Personal Trainer**: Dapatkan rencana latihan yang disusun otomatis oleh AI berdasarkan tujuan (turun berat badan / bentuk otot), tingkat pengalaman, dan ketersediaan alat.
- 🥗 **Nutrisi Cerdas**: Dapatkan rekomendasi makanan, hitung kalori, dan buat *meal plan* sehat yang disesuaikan dengan kebutuhan harian serta alergi makanan Anda.
- 📊 **Tracking Kebugaran**: Pantau indikator kesehatan seperti BMI, kebutuhan kalori harian, dan zona detak jantung secara *real-time* langsung dari *dashboard*.
- 💬 **Asisten AI 24/7**: Chatbot pintar yang siap menjawab pertanyaan seputar olahraga, diet, dan pola hidup sehat kapan saja.

## 🛠️ Teknologi yang Digunakan

Proyek ini dibangun dengan memisahkan *Frontend* dan *Backend* untuk memastikan performa yang cepat, struktur yang bersih, dan skalabilitas yang baik.

### Frontend
- **React 19** (dibangun dengan **Vite**)
- **Tailwind CSS v4** untuk styling yang cepat dan responsif
- **React Router** untuk navigasi halaman (*Single Page Application*)
- **Three.js / React Three Fiber** untuk elemen interaktif/3D 

### Backend
- **FastAPI (Python)** untuk API server yang sangat cepat dan asinkron
- **Google GenAI** sebagai model bahasa (LLM) utama
- **SQLite / SQLAlchemy** untuk penyimpanan data dan *user management*
- **Pandas & NumPy** untuk manipulasi dan analisis dataset besar (data nutrisi dan latihan)
- **Uvicorn** sebagai ASGI web server

---

## 🚀 Cara Menjalankan Proyek Secara Lokal

Pastikan Anda sudah menginstal **Node.js** dan **Python 3.9+** di perangkat Anda.

### 1. Kloning Repositori
```bash
git clone https://github.com/HanifHawari/ProjectPDMLLM.git
cd WebsiteLLM
```

### 2. Menjalankan Backend
```bash
cd backend

# Buat virtual environment (direkomendasikan)
python -m venv venv
# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Instal dependensi Python
pip install -r requirements.txt

# Buat file .env dan isi dengan API Key Anda (seperti kredensial LLM)
# cp .env.example .env (sesuaikan variabel di dalamnya)

# Jalankan server
python main.py
```
*(Secara default, backend FastAPI akan berjalan dan dapat diakses dokumentasi API-nya di `http://localhost:8000/docs`)*

### 3. Menjalankan Frontend
Buka terminal/tab baru dan jalankan:
```bash
cd frontend

# Instal dependensi Node
npm install

# Jalankan frontend server (Vite)
npm run dev
```
*(Buka URL yang ditampilkan di terminal, biasanya `http://localhost:5173` untuk melihat website).*

---

## 👥 Tim Pengembang

Proyek FitMind AI dibangun oleh:
- **M Hanif Hawari** – Backend Developer
- **M Dian Fauzi** – Frontend Developer
- **Adhitya Surya Handika** – AI Engineer
