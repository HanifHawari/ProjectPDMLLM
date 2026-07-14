# Tahap 1: Build Frontend (Node.js)
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend

# Copy dependencies dan install
COPY frontend/package*.json ./
RUN npm install

# Copy seluruh source code frontend dan jalankan build
COPY frontend/ ./
RUN npm run build


# Tahap 2: Setup Backend (Python)
FROM python:3.12-slim
WORKDIR /app

# Install dependencies sistem yang mungkin dibutuhkan (termasuk psycopg2)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy file requirements backend dan install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy source code backend
COPY backend/ ./backend/

# Copy dataset
COPY dataset/ ./dataset/

# Copy hasil build frontend ke dalam backend/dist (agar FastAPI bisa melakukan serve)
COPY --from=frontend-build /app/frontend/dist ./backend/dist

# Konfigurasi Port (Hugging Face Spaces mewajibkan berjalan di port 7860)
ENV PORT=7860
EXPOSE $PORT

# Menjalankan server
WORKDIR /app/backend
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
