FROM python:3.11-slim

WORKDIR /app

# Системные зависимости, как в соседних сервисах
RUN apt-get update \
 && apt-get install -y gcc libpq-dev libffi-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Утилита uv — wrapper для pip / uvicorn
RUN pip install uv

# Копируем и ставим runtime-зависимости
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# (Опционально) Dev-зависимости для локальной разработки / CI
COPY requirements.dev.txt .
# RUN uv pip install --system -r requirements.dev.txt

# Копируем код приложения
COPY ./app ./app

# Запускаем FastAPI через Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
