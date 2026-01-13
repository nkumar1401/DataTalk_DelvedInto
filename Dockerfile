FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Upgrade pip to ensure the latest wheel compatibility
RUN pip install --upgrade pip

# Install requirements with verbose output to see exactly where it fails
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "home.py", "--server.port=8501", "--server.address=0.0.0.0"]