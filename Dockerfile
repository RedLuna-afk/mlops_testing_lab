FROM python:3.10-slim

WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код проекта
COPY . .

# Запуск авто-тестов внутри контейнера при его старте
CMD ["pytest", "-v"]