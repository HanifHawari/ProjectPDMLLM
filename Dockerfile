# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up Python backend with frontend dist
FROM python:3.12-slim
WORKDIR /app/backend

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./

# Copy dataset directory (referenced by the app)
COPY dataset/ /app/dataset/

# Copy built frontend dist into backend/dist (as expected by main.py)
COPY --from=frontend-build /app/frontend/dist ./dist/

# Expose the port Railway provides
EXPOSE ${PORT:-8000}

# Start the FastAPI server
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
