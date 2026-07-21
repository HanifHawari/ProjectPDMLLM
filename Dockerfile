# Setup Backend (Python)
FROM python:3.12-slim
WORKDIR /app

# Install dependencies sistem yang mungkin dibutuhkan
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Trik Hemat Memori: Install PyTorch versi CPU agar ukuran instalasi sangat kecil (~200 MB) dibandingkan versi standar (~2.5 GB)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy file requirements backend dan install sisa dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy source code backend
COPY backend/ ./backend/

# Copy dataset (File CSV mentah yang besar 300MB sudah di-exclude lewat .dockerignore)
COPY dataset/ ./dataset/

# Konfigurasi Railway Port (Railway secara otomatis memberikan environment variable $PORT)
ENV PORT=8000
EXPOSE $PORT

# Menjalankan server
WORKDIR /app/backend
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
