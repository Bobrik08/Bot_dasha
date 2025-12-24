FROM python:3.12-slim

WORKDIR /app

# обновим pip
RUN pip install --no-cache-dir --upgrade pip

# копируем зависимости и ставим их
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# копируем всё приложение
COPY . .

# запускаем бота
CMD ["python", "main.py"]