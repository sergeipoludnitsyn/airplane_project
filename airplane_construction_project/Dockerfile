# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY . /app/

# Запускаем сервер разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]