# FitMind Enterprise Management System 🏋️‍♂️🏢

**FitMind Enterprise Management System** adalah sebuah studi kasus sistem manajemen berskala besar (Enterprise) untuk jaringan *Fitness Center*. Sistem ini menyelesaikan masalah operasional di berbagai divisi berbeda menggunakan pendekatan **Multi-Agentic LLM**. 

Terdapat beberapa divisi (agen) yang saling berinteraksi:
- **Divisi Operasional (Fitness Agent)**: Mengelola dan memberikan rekomendasi seputar fasilitas gym, teknik latihan, dan ketersediaan alat.
- **Divisi F&B (Nutrition Agent)**: Mengatur *meal plan* dan nutrisi klien sesuai dengan alergi dan kondisi kesehatan.
- **Divisi Medis/Klinik (Health Agent)**: Menangani kalkulasi kalori, BMI, zona detak jantung, dan aspek klinis kebugaran.
- **Divisi Perencanaan (Planner Agent)**: Menyusun jadwal komprehensif harian/mingguan.
Semua divisi ini dikoordinasikan secara cerdas oleh **Supervisor Agent** (Manajer Utama).

---

## ✨ Fitur Unggulan

- 🤖 **Enterprise Multi-Agent Architecture**: Dibangun menggunakan *framework* LangChain dengan beberapa agen independen yang mewakili divisi perusahaan.
- 🧠 **Vector Database & RAG (Retrieval-Augmented Generation)**: Pencarian semantik menggunakan **ChromaDB** dan *Embeddings* untuk menarik data secara akurat dari basis data perusahaan.
- 🥗 **Nutrisi & Operasional Cerdas**: Kalkulasi asupan kalori dan *meal plan* sehat yang terintegrasi dengan ketersediaan peralatan gym (*full gym, dumbbell, bodyweight*).
- 💬 **Asisten AI 24/7**: Chatbot manajer yang siap mendelegasikan pertanyaan ke divisi yang tepat.

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
