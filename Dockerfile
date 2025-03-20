# Використовуємо Python 3.10
FROM python:3.10

# Встановлюємо необхідні пакети
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ukr \
    tesseract-ocr-eng

# Встановлюємо локаль для коректної роботи OCR з українською мовою
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Встановлюємо робочу директорію
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо файли бота в контейнер
COPY . .

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Запускаємо бота
CMD ["python", "main.py"]

