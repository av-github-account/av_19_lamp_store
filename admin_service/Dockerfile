# FROM python:3.13-alpine
FROM python:3.11-slim

WORKDIR /app

# RUN apk add --no-cache gcc musl-dev libffi-dev libpq
RUN apt-get update \
 && apt-get install -y gcc libpq-dev libffi-dev curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# # Файл: admin_service/Dockerfile
# ```
# FROM python:3.9-slim

# # Установим рабочую директорию
# WORKDIR /app

# # Копируем файлы зависимостей
# COPY requirements.txt .

# # Устанавливаем зависимости
# RUN pip install --no-cache-dir -r requirements.txt

# # Копируем весь код приложения
# COPY . .

# # Открываем порт
# EXPOSE 8000

# # Запускаем приложение
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# ```
