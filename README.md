# FitMindAI

FitMindAI adalah aplikasi kebugaran dengan landing page, akun pengguna, AI Chat, AI Plan, pencarian latihan dan nutrisi, kalkulator dashboard, serta ekspor rencana ke kalender atau WhatsApp.

## Struktur

- `frontend/` — React 19, Vite, dan React Router.
- `backend/` — FastAPI, SQLAlchemy, layanan AI, dan penyaji hasil build frontend.
- `dataset/` — CSV sumber untuk data latihan, nutrisi, dan program.
- `backend/chroma_db/` — indeks vektor untuk RAG. Jangan hapus tanpa rencana pembuatan ulang.

## Menjalankan secara lokal

1. Salin `backend/.env.example` menjadi `backend/.env`. Isi kunci layanan yang digunakan dan buat `SESSION_SECRET` acak yang panjang. File `.env` tidak boleh dikomit.
2. Buat virtual environment Python di `backend/.venv` dan pasang `backend/requirements.txt`. Jalankan `npm install` di `frontend/`.
3. Jalankan `backend/start.bat` pada Windows, lalu `npm run dev` di `frontend/`.
4. Untuk memperbarui halaman yang disajikan backend, jalankan `npm run build` di `frontend/` dan salin isi `frontend/dist/` ke `backend/dist/`.

Vite memakai proxy `/api` ke `http://localhost:8000`. Jika frontend dan backend ada di origin berbeda, atur `VITE_API_URL` di frontend serta `ALLOWED_ORIGINS` di backend. Backend memakai `DATABASE_URL` jika diset; jika tidak, backend membuat SQLite lokal.

## Keamanan dan data

API akun memakai token sesi. Gunakan `SESSION_SECRET` yang sama pada semua instance backend supaya sesi tetap berlaku setelah restart. Untuk deployment, gunakan HTTPS dan simpan kunci layanan serta kredensial database pada environment server.

File SQLite lokal dapat berisi akun dan percakapan. `.dockerignore` mencegahnya masuk ke image; gunakan `DATABASE_URL` ke penyimpanan persisten di deployment. Endpoint AI, RapidAPI, dan WhatsApp memerlukan pembatasan laju request di lapisan deployment agar tidak disalahgunakan.

## Tim pengembang

- M Hanif Hawari — Backend Developer
- M Dian Fauzi — Frontend Developer
