FROM python:3.13-slim

WORKDIR /app

# отдельно копируем requirements, чтобы докер не пересобирал слои каждый раз
COPY requirements.txt .

# ставим зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# а теперь уже весь остальной код
COPY . .

CMD ["python", "main.py"]